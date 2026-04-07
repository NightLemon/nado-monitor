import os
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None


DEFAULT_MONITORED = ["claude", "node", "python", "code", "cursor", "docker"]


@dataclass
class ClientConfig:
    server_url: str = "http://localhost:8000"
    api_key: str = "change-me-in-production"
    machine_name: str = ""
    os_type: str = ""
    interval_seconds: int = 30
    monitored_processes: list[str] = field(default_factory=lambda: list(DEFAULT_MONITORED))

    def __post_init__(self):
        if not self.machine_name:
            self.machine_name = platform.node()
        if not self.os_type:
            self.os_type = "windows" if sys.platform == "win32" else "linux"

    def validate(self):
        if not self.server_url.startswith("http"):
            raise ValueError(f"server_url must start with http: {self.server_url}")
        if self.interval_seconds <= 0:
            raise ValueError(f"interval_seconds must be > 0: {self.interval_seconds}")
        if not self.machine_name:
            raise ValueError("machine_name cannot be empty")


def load_config(config_path: str | None = None) -> ClientConfig:
    if config_path is None:
        candidates = [
            Path("config.toml"),
            Path(__file__).parent.parent.parent / "config.toml",
        ]
        for c in candidates:
            if c.exists():
                config_path = str(c)
                break

    if config_path and Path(config_path).exists():
        if tomllib is None:
            raise ImportError(
                "Install tomli to use TOML config: pip install nado-telemetry[toml]"
            )
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        config = ClientConfig(
            server_url=data.get("server_url", "http://localhost:8000"),
            api_key=data.get("api_key", "change-me-in-production"),
            machine_name=data.get("machine_name", ""),
            os_type=data.get("os_type", ""),
            interval_seconds=data.get("interval_seconds", 30),
            monitored_processes=data.get("monitored_processes", list(DEFAULT_MONITORED)),
        )
        config.validate()
        return config

    # Fall back to environment variables
    monitored = os.environ.get("NADO_MONITORED_PROCESSES", "")
    config = ClientConfig(
        server_url=os.environ.get("NADO_SERVER_URL", "http://localhost:8000"),
        api_key=os.environ.get("NADO_API_KEY", "change-me-in-production"),
        machine_name=os.environ.get("NADO_MACHINE_NAME", ""),
        os_type=os.environ.get("NADO_OS_TYPE", ""),
        interval_seconds=int(os.environ.get("NADO_INTERVAL", "30")),
        monitored_processes=monitored.split(",") if monitored else list(DEFAULT_MONITORED),
    )
    config.validate()
    return config
