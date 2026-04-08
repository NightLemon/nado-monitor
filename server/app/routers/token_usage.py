from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies import verify_session_token
from ..models import Machine, TokenUsage
from ..schemas import (
    TokenUsageResponse,
    TokenUsageSummary,
    TokenUsageTimePoint,
)

router = APIRouter(tags=["token-usage"], dependencies=[Depends(verify_session_token)])


@router.get("/machines/{machine_id}/token-usage", response_model=TokenUsageResponse)
def get_token_usage(
    machine_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # By project aggregation
    project_rows = (
        db.query(
            TokenUsage.project_path,
            TokenUsage.model,
            func.sum(TokenUsage.input_tokens).label("total_input"),
            func.sum(TokenUsage.output_tokens).label("total_output"),
            func.sum(TokenUsage.cache_creation_tokens).label("total_cache_creation"),
            func.sum(TokenUsage.cache_read_tokens).label("total_cache_read"),
        )
        .filter(TokenUsage.machine_id == machine_id, TokenUsage.timestamp >= cutoff)
        .group_by(TokenUsage.project_path, TokenUsage.model)
        .all()
    )

    by_project = [
        TokenUsageSummary(
            project_path=r.project_path,
            model=r.model,
            total_input_tokens=r.total_input or 0,
            total_output_tokens=r.total_output or 0,
            total_cache_creation_tokens=r.total_cache_creation or 0,
            total_cache_read_tokens=r.total_cache_read or 0,
        )
        for r in project_rows
    ]

    # By time (hourly buckets) — apply timezone offset for display
    offset = get_settings().display_timezone_offset
    offset_modifier = f"+{offset} hours" if offset >= 0 else f"{offset} hours"
    time_rows = (
        db.query(
            func.strftime(
                "%Y-%m-%dT%H:00:00", TokenUsage.timestamp, offset_modifier
            ).label("hour"),
            func.sum(TokenUsage.input_tokens).label("total_input"),
            func.sum(TokenUsage.output_tokens).label("total_output"),
            func.sum(TokenUsage.cache_creation_tokens).label("total_cache_creation"),
            func.sum(TokenUsage.cache_read_tokens).label("total_cache_read"),
        )
        .filter(TokenUsage.machine_id == machine_id, TokenUsage.timestamp >= cutoff)
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    by_time = [
        TokenUsageTimePoint(
            hour=r.hour,
            input_tokens=r.total_input or 0,
            output_tokens=r.total_output or 0,
            cache_creation_tokens=r.total_cache_creation or 0,
            cache_read_tokens=r.total_cache_read or 0,
        )
        for r in time_rows
    ]

    return TokenUsageResponse(
        machine_name=machine.machine_name,
        by_project=by_project,
        by_time=by_time,
    )
