from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    logs: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    stack_trace: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    metrics: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    result: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
