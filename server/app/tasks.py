import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from .database import SessionLocal
from .models import Machine, Telemetry, TokenUsage
from .notifications import send_telegram

logger = logging.getLogger(__name__)


async def cleanup_loop(interval_hours: int, retention_days: int):
    while True:
        await asyncio.sleep(interval_hours * 3600)
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=retention_days)
        try:
            with SessionLocal() as db:
                result = db.execute(
                    delete(Telemetry).where(Telemetry.timestamp < cutoff)
                )
                result2 = db.execute(
                    delete(TokenUsage).where(TokenUsage.timestamp < cutoff)
                )
                db.commit()
                logger.info(
                    f"Cleaned up {result.rowcount} telemetry + "
                    f"{result2.rowcount} token_usage records"
                )
        except Exception:
            logger.exception("Error during telemetry cleanup")


async def alert_loop(bot_token: str, chat_id: str, waiting_minutes: int):
    """Check for sessions waiting too long and send Telegram alerts."""
    if not bot_token or not chat_id:
        logger.info("Telegram not configured, alert_loop disabled")
        return

    # Track already-alerted sessions to avoid spam
    alerted: set[str] = set()
    threshold = timedelta(minutes=waiting_minutes)

    while True:
        await asyncio.sleep(60)
        try:
            now = datetime.now(timezone.utc)
            with SessionLocal() as db:
                machines = db.query(Machine).all()

                new_waiting: set[str] = set()
                for machine in machines:
                    try:
                        sessions = json.loads(machine.session_status or "[]")
                    except Exception:
                        continue

                    for s in sessions:
                        status = s.get("status", "")
                        if status not in ("waiting_tool", "waiting_input"):
                            continue

                        last_activity = s.get("last_activity", "")
                        if not last_activity:
                            continue

                        try:
                            activity_time = datetime.fromisoformat(
                                last_activity.replace("Z", "+00:00")
                            )
                        except ValueError:
                            continue

                        wait_duration = now - activity_time
                        if wait_duration < threshold:
                            continue

                        # Build unique key for this waiting session
                        key = f"{machine.machine_name}:{s.get('session_id', '')}"
                        new_waiting.add(key)

                        if key in alerted:
                            continue

                        # Extract display info
                        project = s.get("project_path", "unknown")
                        # Shorten project path: "c--Users-lxiang-repos-nado-monitor" -> "nado-monitor"
                        repos_idx = project.find("-repos-")
                        if repos_idx >= 0:
                            project = project[repos_idx + 7:]

                        model = s.get("model", "unknown")
                        if model.startswith("claude-"):
                            model = model[7:]

                        status_label = (
                            "waiting for authorization"
                            if status == "waiting_tool"
                            else "waiting for input"
                        )
                        minutes = int(wait_duration.total_seconds() / 60)

                        text = (
                            f"\u26a0\ufe0f <b>[{machine.machine_name}]</b>\n"
                            f"Session {status_label} ({minutes} min)\n"
                            f"Project: {project} | Model: {model}"
                        )
                        await send_telegram(bot_token, chat_id, text)
                        alerted.add(key)

            # Remove alerts for sessions no longer waiting
            alerted = alerted & new_waiting

        except Exception:
            logger.exception("Error in alert_loop")
