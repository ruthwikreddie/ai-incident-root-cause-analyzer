from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    logs: str = Field(
        min_length=1,
        description="Application or service logs from the incident.",
    )

    stack_trace: str = Field(
        default="",
        description="Optional stack trace associated with the incident.",
    )

    metrics: str = Field(
        default="",
        description="Optional infrastructure or application metrics.",
    )


class IncidentAnalysis(BaseModel):
    root_cause: str

    affected_services: list[str] = Field(
        default_factory=list,
    )

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]

    fix_recommendation: str

    postmortem_summary: str


class IncidentResponse(BaseModel):
    id: int
    created_at: datetime
    analysis: IncidentAnalysis
