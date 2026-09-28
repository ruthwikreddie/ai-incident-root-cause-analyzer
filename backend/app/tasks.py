import logging

from .database import SessionLocal
from .models import Incident
from .services.analyzer import analyze_incident


logger = logging.getLogger(__name__)


def process_incident(incident_id: int) -> None:
    db = SessionLocal()

    try:
        incident = db.get(Incident, incident_id)

        if incident is None:
            raise ValueError(
                f"Incident {incident_id} does not exist."
            )

        incident.status = "processing"
        incident.error_message = None
        db.commit()

        analysis = analyze_incident(
            logs=incident.logs,
            stack_trace=incident.stack_trace,
            metrics=incident.metrics,
        )

        incident.result = analysis.model_dump_json()
        incident.status = "completed"
        incident.error_message = None

        db.commit()

    except Exception as exc:
        db.rollback()

        incident = db.get(Incident, incident_id)

        if incident is not None:
            incident.status = "failed"
            incident.error_message = str(exc)[:2000]
            db.commit()

        logger.exception(
            "Incident %s analysis failed.",
            incident_id,
        )

        raise

    finally:
        db.close()
