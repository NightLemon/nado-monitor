import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

STATE_FILE = Path.home() / ".nado_telemetry_state.json"


def _load_offsets() -> dict[str, int]:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("Failed to load state file, starting fresh")
    return {}


def _save_offsets(offsets: dict[str, int]):
    try:
        STATE_FILE.write_text(json.dumps(offsets), encoding="utf-8")
    except Exception:
        logger.warning("Failed to save state file")


def _scan_jsonl(file_path: Path, offset: int) -> tuple[list[dict], int]:
    """Read new lines from a JSONL file starting at byte offset.
    Returns (entries, new_offset)."""
    entries = []
    try:
        size = file_path.stat().st_size
        if size <= offset:
            return entries, offset

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(offset)
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    # Possibly a partial write — stop here, retry next cycle
                    break

                msg = data.get("message", {})
                usage = msg.get("usage")
                if msg.get("role") == "assistant" and usage:
                    entries.append({
                        "input_tokens": usage.get("input_tokens") or 0,
                        "output_tokens": usage.get("output_tokens") or 0,
                        "cache_creation_tokens": usage.get("cache_creation_input_tokens") or 0,
                        "cache_read_tokens": usage.get("cache_read_input_tokens") or 0,
                        "model": msg.get("model") or "unknown",
                    })
            new_offset = f.tell()
    except (OSError, PermissionError) as e:
        logger.debug(f"Cannot read {file_path}: {e}")
        return entries, offset

    return entries, new_offset


def collect_claude_tokens(projects_dir: Path) -> list[dict]:
    """Scan Claude Code JSONL files and return delta token usage entries."""
    if not projects_dir.exists():
        return []

    offsets = _load_offsets()
    results: dict[tuple, dict] = {}  # (project, session, model) -> aggregated

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name

        # Find all JSONL files (conversations + subagents)
        jsonl_files = list(project_dir.glob("**/*.jsonl"))

        for jsonl_file in jsonl_files:
            file_key = str(jsonl_file)
            old_offset = offsets.get(file_key, 0)
            entries, new_offset = _scan_jsonl(jsonl_file, old_offset)
            offsets[file_key] = new_offset

            if not entries:
                continue

            # Derive session_id from the filename (UUID part)
            session_id = jsonl_file.stem

            for entry in entries:
                key = (project_name, session_id, entry["model"])
                if key not in results:
                    results[key] = {
                        "project_path": project_name,
                        "session_id": session_id,
                        "model": entry["model"],
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cache_creation_tokens": 0,
                        "cache_read_tokens": 0,
                    }
                agg = results[key]
                agg["input_tokens"] += entry["input_tokens"] or 0
                agg["output_tokens"] += entry["output_tokens"] or 0
                agg["cache_creation_tokens"] += entry["cache_creation_tokens"] or 0
                agg["cache_read_tokens"] += entry["cache_read_tokens"] or 0

    _save_offsets(offsets)

    return list(results.values())
