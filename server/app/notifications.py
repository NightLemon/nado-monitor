import logging

import httpx

logger = logging.getLogger(__name__)


async def send_telegram(bot_token: str, chat_id: str, text: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            })
            if resp.status_code == 200:
                return True
            logger.warning(f"Telegram API returned {resp.status_code}: {resp.text}")
            return False
    except Exception:
        logger.exception("Failed to send Telegram notification")
        return False
