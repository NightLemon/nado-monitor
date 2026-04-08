import type { SessionStatus } from "@/types";
import { toDisplayTime } from "@/utils/time";

interface SessionStatusPanelProps {
  sessions: SessionStatus[];
}

const STATUS_CONFIG: Record<
  string,
  { label: string; dotClass: string; badgeClass: string }
> = {
  waiting_tool: {
    label: "Waiting Auth",
    dotClass: "bg-amber-400 animate-pulse",
    badgeClass: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  },
  waiting_input: {
    label: "Waiting Input",
    dotClass: "bg-blue-400",
    badgeClass: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  },
  running: {
    label: "Running",
    dotClass: "bg-emerald-400",
    badgeClass: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  },
  idle: {
    label: "Idle",
    dotClass: "bg-slate-500",
    badgeClass: "bg-slate-500/15 text-slate-400 border-slate-500/20",
  },
};

function shortProject(path: string): string {
  // "c--Users-lxiang-repos-nado-monitor" -> "nado-monitor"
  // Find the part after "repos-" if present, otherwise last meaningful segment
  const reposIdx = path.indexOf("-repos-");
  if (reposIdx >= 0) {
    return path.slice(reposIdx + 7); // skip "-repos-"
  }
  return path;
}

function shortModel(model: string): string {
  // "claude-opus-4-6" -> "opus-4-6"
  return model.replace(/^claude-/, "");
}

function formatActivityTime(isoStr: string): string {
  // isoStr can be "2026-04-08T15:41:01.859000+00:00" or with "Z"
  const d = toDisplayTime(isoStr.replace(/\+00:00$/, "Z"));
  const h = d.getUTCHours().toString().padStart(2, "0");
  const m = d.getUTCMinutes().toString().padStart(2, "0");
  return `${h}:${m}`;
}

export function SessionStatusPanel({ sessions }: SessionStatusPanelProps) {
  if (!sessions || sessions.length === 0) return null;

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">
        Active Sessions
      </h3>
      <div className="space-y-2">
        {sessions.map((s) => {
          const cfg = STATUS_CONFIG[s.status] || STATUS_CONFIG.idle;
          return (
            <div
              key={`${s.project_path}-${s.session_id}`}
              className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-750 hover:bg-slate-700/50 transition-colors"
              style={{ backgroundColor: "rgba(30,41,59,0.5)" }}
            >
              <div className="flex items-center gap-3 min-w-0">
                <span
                  className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs border ${cfg.badgeClass}`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${cfg.dotClass}`}
                  />
                  {cfg.label}
                </span>
                <span className="text-sm text-white truncate">
                  {s.slug || shortProject(s.project_path)}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500 shrink-0">
                {s.model && (
                  <span className="text-slate-400">{shortModel(s.model)}</span>
                )}
                {s.last_activity && (
                  <span>{formatActivityTime(s.last_activity)}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
