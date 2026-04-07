import psutil


def detect_processes(monitored: list[str]) -> list[dict]:
    found = []
    seen: set[tuple[str, int]] = set()

    for proc in psutil.process_iter(["pid", "name", "status"]):
        try:
            info = proc.info
            name_lower = info["name"].lower()
            matched = False

            for target in monitored:
                if target in name_lower:
                    key = (target, info["pid"])
                    if key not in seen:
                        seen.add(key)
                        found.append(
                            {
                                "name": target,
                                "pid": info["pid"],
                                "process_name": info["name"],
                                "status": info["status"],
                            }
                        )
                    matched = True
                    break

            # Also check command line for matches not found in process name
            if not matched:
                try:
                    cmdline = " ".join(proc.cmdline()).lower()
                except (psutil.AccessDenied, OSError):
                    continue
                for target in monitored:
                    if target in cmdline:
                        key = (target, info["pid"])
                        if key not in seen:
                            seen.add(key)
                            found.append(
                                {
                                    "name": target,
                                    "pid": info["pid"],
                                    "process_name": info["name"],
                                    "status": info["status"],
                                }
                            )
                        break

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return found
