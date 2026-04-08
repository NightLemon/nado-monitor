import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies import verify_session_token
from ..models import Machine, Telemetry
from ..schemas import HistoryPoint, HistoryResponse, LatestMetrics, MachineOut

router = APIRouter(tags=["machines"], dependencies=[Depends(verify_session_token)])


def _is_online(last_heartbeat: datetime) -> bool:
    timeout = timedelta(seconds=get_settings().heartbeat_timeout_seconds)
    # SQLite stores naive datetimes; treat them as UTC
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


def _machine_to_out(machine: Machine, latest: Telemetry | None) -> MachineOut:
    return MachineOut(
        id=machine.id,
        machine_name=machine.machine_name,
        os_type=machine.os_type,
        is_online=_is_online(machine.last_heartbeat),
        last_heartbeat=machine.last_heartbeat,
        first_seen=machine.first_seen,
        latest_metrics=_build_latest_metrics(latest),
    )


@router.get("/machines", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db)):
    machines = db.query(Machine).all()
    result = []
    for m in machines:
        latest = (
            db.query(Telemetry)
            .filter(Telemetry.machine_id == m.id)
            .order_by(desc(Telemetry.timestamp))
            .first()
        )
        result.append(_machine_to_out(m, latest))
    return result


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
    return _machine_to_out(machine, latest)


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
