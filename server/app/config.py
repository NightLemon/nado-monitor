from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./nado_monitor.db"
    api_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173"
    heartbeat_timeout_seconds: int = 90
    retention_days: int = 7
    cleanup_interval_hours: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
