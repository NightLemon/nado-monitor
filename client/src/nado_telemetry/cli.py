import argparse
import logging
import time
from pathlib import Path

import httpx

from .collectors.claude_tokens import collect_claude_tokens
from .collectors.processes import detect_processes
from .collectors.system import collect_system_metrics
from .config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run(config_path: str | None = None):
    config = load_config(config_path)
    logger.info(
        f"Starting telemetry client: machine={config.machine_name}, "
        f"os={config.os_type}, server={config.server_url}, "
        f"interval={config.interval_seconds}s"
    )

    consecutive_failures = 0

    while True:
        try:
            metrics = collect_system_metrics()
            processes = detect_processes(config.monitored_processes)

            token_usage = []
            if config.track_claude_tokens:
                token_usage = collect_claude_tokens(Path(config.claude_projects_dir))

            payload = {
                "machine_name": config.machine_name,
                "os_type": config.os_type,
                **metrics,
                "processes": processes,
                "token_usage": token_usage,
            }

            response = httpx.post(
                f"{config.server_url}/api/telemetry",
                json=payload,
                headers={"X-API-Key": config.api_key},
                timeout=10,
            )
            response.raise_for_status()
            consecutive_failures = 0
            logger.info(
                f"Sent: cpu={metrics['cpu_percent']}%, "
                f"mem={metrics['memory_percent']}%, "
                f"procs={len(processes)}, "
                f"token_entries={len(token_usage)}"
            )

        except httpx.HTTPError as e:
            consecutive_failures += 1
            logger.warning(f"HTTP error ({consecutive_failures}): {e}")
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Failed ({consecutive_failures}): {e}")

        # Back off on repeated failures (max 5 min)
        sleep_time = config.interval_seconds
        if consecutive_failures > 3:
            sleep_time = min(sleep_time * consecutive_failures, 300)
            logger.info(f"Backing off: next attempt in {sleep_time}s")

        time.sleep(sleep_time)


def main():
    parser = argparse.ArgumentParser(description="Nado Telemetry Client")
    parser.add_argument(
        "-c", "--config", help="Path to config.toml file", default=None
    )
    args = parser.parse_args()

    try:
        run(args.config)
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
