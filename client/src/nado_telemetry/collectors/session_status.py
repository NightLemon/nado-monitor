import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

STALE_THRESHOLD = 3600  # 1 hour — older than this = skip entirely
TAIL_BYTES = 16384  # read last 16KB to get enough context

# Entry types that represent real conversation turns
TURN_TYPES = {"user", "assistant"}


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

    # Walk backwards through entries to find the last conversation turn
    slug = ""
    model = ""
    last_turn_type = None  # "user" or "assistant"
    last_assistant_stop = None  # stop_reason of the last assistant before any user
    found_user_after_assistant = False

    for raw in reversed(lines):
        if not raw.startswith("{"):
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get("type")

        # Extract slug from any entry that has it
        if not slug:
            slug = entry.get("slug", "")

        if entry_type not in TURN_TYPES:
            continue

        if entry_type == "user" and last_turn_type is None:
            last_turn_type = "user"
            # If we already found an assistant, this user came after it
            if last_assistant_stop is not None:
                found_user_after_assistant = True

        if entry_type == "assistant":
            msg = entry.get("message") or {}
            if not model:
                model = msg.get("model") or entry.get("model") or ""
            stop = entry.get("stop_reason") or msg.get("stop_reason")
            if last_assistant_stop is None:
                last_assistant_stop = stop
            if last_turn_type is None:
                last_turn_type = "assistant"

        # Once we have slug + model + turn info, we're done
        if slug and model and last_turn_type:
            break

    if not last_turn_type:
        return None

    # Determine status based on content, not mtime
    if last_turn_type == "user":
        # Last turn was user — AI is processing or user sent tool_result
        status = "running"
    elif last_turn_type == "assistant":
        if last_assistant_stop == "tool_use":
            if found_user_after_assistant:
                # tool_use followed by user (tool_result) = still processing
                status = "running"
            else:
                status = "waiting_tool"
        elif last_assistant_stop == "end_turn":
            status = "waiting_input"
        else:
            status = "running"
    else:
        status = "idle"

    # Only mark as idle if file is truly stale (>10 min) AND status would be waiting
    if age > 600 and status in ("waiting_input", "waiting_tool"):
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
