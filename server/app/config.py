from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./nado_monitor.db"
    api_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173"
    heartbeat_timeout_seconds: int = 90
    retention_days: int = 7
    cleanup_interval_hours: int = 1

    # TOTP auth for dashboard viewers (empty = auth disabled)
    totp_secret: str = ""
    session_token_secret: str = ""
    session_token_expiry_hours: int = 24

    # Display timezone offset from UTC (hours), e.g. 8 for Asia/Shanghai
    display_timezone_offset: int = 8

    # Telegram notifications
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    alert_waiting_minutes: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        # Auto-generate session token secret if not set
        if not _settings.session_token_secret:
            import os
            _settings.session_token_secret = os.urandom(32).hex()
    return _settings
