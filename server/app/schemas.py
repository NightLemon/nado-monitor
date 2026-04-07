import json
from datetime import datetime

from pydantic import BaseModel, field_validator


class ProcessInfo(BaseModel):
    name: str
    pid: int
    process_name: str
    status: str


class TelemetryPayload(BaseModel):
    machine_name: str
    os_type: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    processes: list[ProcessInfo] = []


class LatestMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    processes: list[ProcessInfo]
    timestamp: datetime


class MachineOut(BaseModel):
    id: int
    machine_name: str
    os_type: str
    is_online: bool
    last_heartbeat: datetime
    first_seen: datetime
    latest_metrics: LatestMetrics | None = None

    model_config = {"from_attributes": True}


class HistoryPoint(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float


class HistoryResponse(BaseModel):
    machine_name: str
    data_points: list[HistoryPoint]
