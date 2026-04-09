import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies import verify_session_token
from ..models import Machine, Telemetry, TokenUsage
from ..schemas import (
    HistoryPoint,
    HistoryResponse,
    LatestMetrics,
    MachineOut,
    SessionStatusEntry,
    TodayTokens,
)

router = APIRouter(tags=["machines"], dependencies=[Depends(verify_session_token)])


def _is_online(last_heartbeat: datetime) -> bool:
    timeout = timedelta(seconds=get_settings().heartbeat_timeout_seconds)
    if last_heartbeat.tzinfo is None:
        last_heartbeat = last_heartbeat.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last_heartbeat < timeout


def _build_latest_metrics(t: Telemetry | None) -> LatestMetrics | None:
    if t is None:
        return None
    return LatestMetrics(
        cpu_percent=t.cpu_percent,
        memory_percent=t.memory_percent,
        memory_used_gb=t.memory_used_gb,
        memory_total_gb=t.memory_total_gb,
        disk_percent=t.disk_percent,
        disk_used_gb=t.disk_used_gb,
        disk_total_gb=t.disk_total_gb,
        processes=json.loads(t.processes),
        timestamp=t.timestamp,
    )


def _machine_to_out(
    machine: Machine,
    latest: Telemetry | None,
    today_tokens: TodayTokens | None = None,
) -> MachineOut:
    try:
        sessions = [SessionStatusEntry(**s) for s in json.loads(machine.session_status or "[]")]
    except Exception:
        sessions = []
    return MachineOut(
        id=machine.id,
        machine_name=machine.machine_name,
        os_type=machine.os_type,
        is_online=_is_online(machine.last_heartbeat),
        last_heartbeat=machine.last_heartbeat,
        first_seen=machine.first_seen,
        latest_metrics=_build_latest_metrics(latest),
        session_status=sessions,
        today_tokens=today_tokens or TodayTokens(),
    )


@router.get("/machines", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db)):
    # Single query: latest telemetry per machine via subquery
    latest_sub = (
        db.query(
            Telemetry.machine_id,
            func.max(Telemetry.id).label("max_id"),
        )
        .group_by(Telemetry.machine_id)
        .subquery()
    )

    rows = (
        db.query(Machine, Telemetry)
        .outerjoin(latest_sub, Machine.id == latest_sub.c.machine_id)
        .outerjoin(Telemetry, Telemetry.id == latest_sub.c.max_id)
        .all()
    )

    # Today's token totals per machine (SQLite stores naive UTC datetimes)
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    token_rows = (
        db.query(
            TokenUsage.machine_id,
            func.sum(TokenUsage.input_tokens).label("input"),
            func.sum(TokenUsage.output_tokens).label("output"),
            func.sum(TokenUsage.cache_read_tokens).label("cache_read"),
            func.sum(TokenUsage.cache_creation_tokens).label("cache_creation"),
        )
        .filter(TokenUsage.timestamp >= today_start)
        .group_by(TokenUsage.machine_id)
        .all()
    )
    token_map = {
        r.machine_id: TodayTokens(
            input=r.input or 0,
            output=r.output or 0,
            cache_read=r.cache_read or 0,
            cache_creation=r.cache_creation or 0,
        )
        for r in token_rows
    }

    return [
        _machine_to_out(m, t, token_map.get(m.id))
        for m, t in rows
    ]


@router.get("/machines/{machine_id}", response_model=MachineOut)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    latest = (
        db.query(Telemetry)
        .filter(Telemetry.machine_id == machine.id)
        .order_by(desc(Telemetry.timestamp))
        .first()
    )

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    token_row = (
        db.query(
            func.sum(TokenUsage.input_tokens).label("input"),
            func.sum(TokenUsage.output_tokens).label("output"),
            func.sum(TokenUsage.cache_read_tokens).label("cache_read"),
            func.sum(TokenUsage.cache_creation_tokens).label("cache_creation"),
        )
        .filter(TokenUsage.machine_id == machine_id, TokenUsage.timestamp >= today_start)
        .first()
    )
    today_tokens = None
    if token_row and token_row.input is not None:
        today_tokens = TodayTokens(
            input=token_row.input or 0,
            output=token_row.output or 0,
            cache_read=token_row.cache_read or 0,
            cache_creation=token_row.cache_creation or 0,
        )

    return _machine_to_out(machine, latest, today_tokens)


@router.get("/machines/{machine_id}/history", response_model=HistoryResponse)
def get_machine_history(
    machine_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    rows = (
        db.query(Telemetry)
        .filter(Telemetry.machine_id == machine_id, Telemetry.timestamp >= cutoff)
        .order_by(Telemetry.timestamp)
        .all()
    )

    # Downsample if too many points (>500)
    if len(rows) > 500:
        step = len(rows) // 500
        rows = rows[::step]

    data_points = [
        HistoryPoint(
            timestamp=r.timestamp,
            cpu_percent=r.cpu_percent,
            memory_percent=r.memory_percent,
            disk_percent=r.disk_percent,
        )
        for r in rows
    ]

    return HistoryResponse(machine_name=machine.machine_name, data_points=data_points)
