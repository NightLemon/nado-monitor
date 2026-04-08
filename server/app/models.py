from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    os_type: Mapped[str] = mapped_column(String, nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    first_seen: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    session_status: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    telemetry: Mapped[list["Telemetry"]] = relationship(
        back_populates="machine", cascade="all, delete-orphan"
    )
    token_usage: Mapped[list["TokenUsage"]] = relationship(
        back_populates="machine", cascade="all, delete-orphan"
    )


class Telemetry(Base):
    __tablename__ = "telemetry"
    __table_args__ = (Index("ix_telemetry_machine_timestamp", "machine_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_used_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_total_gb: Mapped[float] = mapped_column(Float, nullable=False)
    disk_percent: Mapped[float] = mapped_column(Float, nullable=False)
    disk_used_gb: Mapped[float] = mapped_column(Float, nullable=False)
    disk_total_gb: Mapped[float] = mapped_column(Float, nullable=False)
    processes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    machine: Mapped["Machine"] = relationship(back_populates="telemetry")


class TokenUsage(Base):
    __tablename__ = "token_usage"
    __table_args__ = (
        Index("ix_token_usage_machine_timestamp", "machine_id", "timestamp"),
        Index("ix_token_usage_project", "machine_id", "project_path"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    project_path: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cache_creation_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    machine: Mapped["Machine"] = relationship(back_populates="token_usage")
