from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import Response
from rq import Retry
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Incident
from ...queue import incident_queue
from ...schemas import (
    IncidentAnalysis,
    IncidentRequest,
    IncidentResponse,
)
from ...services.pdf_report import build_pdf
from ...tasks import process_incident


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["incidents"],
)


def to_response(incident: Incident) -> IncidentResponse:
    analysis = None

    if incident.result:
        analysis = IncidentAnalysis.model_validate_json(
            incident.result
        )

    return IncidentResponse(
        id=incident.id,
        status=incident.status,
        job_id=incident.job_id,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        analysis=analysis,
        error_message=incident.error_message,
    )


@router.post(
    "/analyze",
    response_model=IncidentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def analyze(
    payload: IncidentRequest,
    db: Session = Depends(get_db),
):
    incident = Incident(
        logs=payload.logs,
        stack_trace=payload.stack_trace,
        metrics=payload.metrics,
        status="queued",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    job_id = f"incident-{incident.id}"
    incident.job_id = job_id
    db.commit()

    try:
        incident_queue.enqueue(
            process_incident,
            incident.id,
            job_id=job_id,
            job_timeout=120,
            result_ttl=3600,
            failure_ttl=86400,
            retry=Retry(
                max=3,
                interval=[5, 15, 30],
            ),
        )

    except Exception as exc:
        incident.status = "failed"
        incident.error_message = (
            f"Unable to enqueue analysis job: {exc}"
        )
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Incident analysis queue unavailable.",
        )

    db.refresh(incident)

    return to_response(incident)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = (
        select(Incident)
        .order_by(Incident.created_at.desc())
        .limit(limit)
    )

    incidents = db.scalars(statement).all()

    return [to_response(i) for i in incidents]


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return to_response(incident)


@router.get("/{incident_id}/pdf")
def get_incident_pdf(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    if incident.status != "completed" or not incident.result:
        raise HTTPException(
            status_code=409,
            detail="Incident analysis is not complete.",
        )

    analysis = IncidentAnalysis.model_validate_json(
        incident.result
    )

    pdf_bytes = build_pdf(analysis)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="incident-{incident_id}.pdf"'
        },
    )
