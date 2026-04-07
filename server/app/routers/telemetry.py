import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import verify_api_key
from ..models import Machine, Telemetry
from ..schemas import TelemetryPayload

logger = logging.getLogger(__name__)
router = APIRouter(tags=["telemetry"])


@router.post("/telemetry", status_code=201, dependencies=[Depends(verify_api_key)])
def ingest_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # Upsert machine with retry on unique constraint race
    machine = db.query(Machine).filter(Machine.machine_name == payload.machine_name).first()
    if machine is None:
        try:
            machine = Machine(
                machine_name=payload.machine_name,
                os_type=payload.os_type,
                last_heartbeat=now,
                first_seen=now,
            )
            db.add(machine)
            db.flush()
        except IntegrityError:
            db.rollback()
            machine = db.query(Machine).filter(
                Machine.machine_name == payload.machine_name
            ).first()
            machine.last_heartbeat = now
            machine.os_type = payload.os_type
    else:
        machine.last_heartbeat = now
        machine.os_type = payload.os_type

    telemetry = Telemetry(
        machine_id=machine.id,
        timestamp=now,
        cpu_percent=payload.cpu_percent,
        memory_percent=payload.memory_percent,
        memory_used_gb=payload.memory_used_gb,
        memory_total_gb=payload.memory_total_gb,
        disk_percent=payload.disk_percent,
        disk_used_gb=payload.disk_used_gb,
        disk_total_gb=payload.disk_total_gb,
        processes=json.dumps([p.model_dump() for p in payload.processes]),
    )
    db.add(telemetry)
    db.commit()

    return {"status": "ok"}
