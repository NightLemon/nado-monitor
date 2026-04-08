import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Thresholds in seconds
ACTIVE_THRESHOLD = 120  # 2 minutes — file modified within this = active session
STALE_THRESHOLD = 3600  # 1 hour — older than this = skip entirely
TAIL_BYTES = 8192  # read last 8KB of file to find recent entries


def _read_tail_lines(file_path: Path, num_bytes: int = TAIL_BYTES) -> list[str]:
    """Read the last num_bytes of a file and return parsed lines."""
    try:
        size = file_path.stat().st_size
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            if size > num_bytes:
                f.seek(size - num_bytes)
                f.readline()  # discard partial first line
            lines = f.readlines()
        return [ln.strip() for ln in lines if ln.strip()]
    except (OSError, PermissionError):
        return []


def _parse_session(file_path: Path, project_name: str, now: float) -> dict | None:
    """Parse a JSONL session file and return status info, or None if stale."""
    try:
        mtime = file_path.stat().st_mtime
    except OSError:
        return None

    age = now - mtime
    if age >= STALE_THRESHOLD:
        return None

    lines = _read_tail_lines(file_path)
    if not lines:
        return None

    # Parse last entries to determine state
    last_assistant = None
    last_type = None
    slug = ""
    model = ""

    for raw in reversed(lines):
        if not raw.startswith("{"):
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get("type")

        # Extract slug from any recent entry that has it
        if not slug:
            slug = entry.get("slug", "")

        if entry_type == "assistant" and last_assistant is None:
            last_assistant = entry
            msg = entry.get("message") or {}
            model = msg.get("model") or entry.get("model") or ""
            if not last_type:
                last_type = "assistant"

        elif entry_type == "user" and last_type is None:
            last_type = "user"

        # Once we have both pieces, stop scanning
        if last_type and last_assistant and slug:
            break

    # Determine status
    if age < ACTIVE_THRESHOLD:
        if last_type == "assistant" and last_assistant:
            stop_reason = last_assistant.get("stop_reason") or (
                last_assistant.get("message", {}).get("stop_reason")
            )
            if stop_reason == "tool_use":
                status = "waiting_tool"
            elif stop_reason == "end_turn":
                status = "waiting_input"
            else:
                status = "running"
        elif last_type == "user":
            status = "running"
        else:
            status = "running"
    else:
        status = "idle"

    last_activity = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

    return {
        "project_path": project_name,
        "session_id": file_path.stem,
        "status": status,
        "model": model,
        "last_activity": last_activity,
        "slug": slug,
    }


def collect_session_status(projects_dir: Path) -> list[dict]:
    """Scan Claude Code JSONL files and return current session statuses."""
    if not projects_dir.exists():
        return []

    now = time.time()
    results = []

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name

        # Scan root-level JSONL files (main sessions)
        jsonl_files = list(project_dir.glob("*.jsonl"))
        # Also scan one-level UUID subdirectories (but not subagents/)
        for subdir in project_dir.iterdir():
            if subdir.is_dir() and subdir.name != "subagents":
                jsonl_files.extend(subdir.glob("*.jsonl"))

        for jsonl_file in jsonl_files:
            info = _parse_session(jsonl_file, project_name, now)
            if info:
                results.append(info)

    # Sort: waiting sessions first, then running, then idle
    status_order = {"waiting_tool": 0, "waiting_input": 1, "running": 2, "idle": 3}
    results.sort(key=lambda r: status_order.get(r["status"], 9))

    return results
