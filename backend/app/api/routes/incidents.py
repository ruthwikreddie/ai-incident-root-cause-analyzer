import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Incident
from ...schemas import (
    IncidentAnalysis,
    IncidentRequest,
    IncidentResponse,
)
from ...services.analyzer import analyze_incident
from ...services.pdf_report import build_pdf


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["incidents"],
)


def to_response(
    incident: Incident,
) -> IncidentResponse:

    analysis = IncidentAnalysis.model_validate_json(
        incident.result
    )

    return IncidentResponse(
        id=incident.id,
        created_at=incident.created_at,
        analysis=analysis,
    )


@router.post(
    "/analyze",
    response_model=IncidentResponse,
    status_code=201,
)
def analyze(
    payload: IncidentRequest,
    db: Session = Depends(get_db),
):

    analysis = analyze_incident(
        logs=payload.logs,
        stack_trace=payload.stack_trace,
        metrics=payload.metrics,
    )

    incident = Incident(
        logs=payload.logs,
        stack_trace=payload.stack_trace,
        metrics=payload.metrics,
        result=analysis.model_dump_json(),
    )

    try:
        db.add(incident)
        db.commit()
        db.refresh(incident)

    except Exception:
        db.rollback()
        raise

    return to_response(incident)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):

    statement = (
        select(Incident)
        .order_by(Incident.created_at.desc())
        .limit(limit)
    )

    incidents = db.scalars(statement).all()

    return [
        to_response(incident)
        for incident in incidents
    ]


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):

    incident = db.get(
        Incident,
        incident_id,
    )

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

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
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
