import json
from datetime import datetime

from pydantic import BaseModel, field_validator


class ProcessInfo(BaseModel):
    name: str
    pid: int
    process_name: str
    status: str


class TokenUsageEntry(BaseModel):
    project_path: str
    session_id: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0


class SessionStatusEntry(BaseModel):
    project_path: str
    session_id: str
    status: str  # running | waiting_tool | waiting_input | idle
    model: str = ""
    last_activity: str = ""
    slug: str = ""


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
    token_usage: list[TokenUsageEntry] = []
    session_status: list[SessionStatusEntry] = []


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


class TodayTokens(BaseModel):
    input: int = 0
    output: int = 0
    cache_read: int = 0
    cache_creation: int = 0


class MachineOut(BaseModel):
    id: int
    machine_name: str
    os_type: str
    is_online: bool
    last_heartbeat: datetime
    first_seen: datetime
    latest_metrics: LatestMetrics | None = None
    session_status: list[SessionStatusEntry] = []
    today_tokens: TodayTokens = TodayTokens()

    model_config = {"from_attributes": True}


class HistoryPoint(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float


class HistoryResponse(BaseModel):
    machine_name: str
    data_points: list[HistoryPoint]


class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    expires_in: int


class TokenUsageSummary(BaseModel):
    project_path: str
    model: str
    total_input_tokens: int
    total_output_tokens: int
    total_cache_creation_tokens: int
    total_cache_read_tokens: int


class TokenUsageTimePoint(BaseModel):
    hour: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int


class TokenUsageResponse(BaseModel):
    machine_name: str
    by_project: list[TokenUsageSummary]
    by_time: list[TokenUsageTimePoint]
