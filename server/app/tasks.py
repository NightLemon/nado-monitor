import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from .database import SessionLocal
from .models import Telemetry

logger = logging.getLogger(__name__)


async def cleanup_loop(interval_hours: int, retention_days: int):
    while True:
        await asyncio.sleep(interval_hours * 3600)
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        try:
            with SessionLocal() as db:
                result = db.execute(
                    delete(Telemetry).where(Telemetry.timestamp < cutoff)
                )
                db.commit()
                logger.info(f"Cleaned up {result.rowcount} old telemetry records")
        except Exception:
            logger.exception("Error during telemetry cleanup")
