import type { ProcessInfo } from "@/types";
import { DEFAULT_MONITORED_PROCESSES } from "@/constants";

interface ProcessListProps {
  processes: ProcessInfo[];
  monitored?: string[];
}

export function ProcessList({ processes, monitored }: ProcessListProps) {
  const targets = monitored ?? [...DEFAULT_MONITORED_PROCESSES];

  // Group processes by target name
  const grouped = new Map<string, ProcessInfo[]>();
  for (const p of processes) {
    const list = grouped.get(p.name) ?? [];
    list.push(p);
    grouped.set(p.name, list);
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
        Agent & Tool Status
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {targets.map((target) => {
          const procs = grouped.get(target);
          const isRunning = procs && procs.length > 0;

          return (
            <div
              key={target}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                isRunning
                  ? "border-emerald-500/30 bg-emerald-500/5"
                  : "border-slate-700 bg-slate-800/50"
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  isRunning ? "bg-emerald-400" : "bg-slate-600"
                }`}
              />
              <div className="min-w-0">
                <span className="text-sm font-medium text-slate-200 capitalize">
                  {target}
                </span>
                {isRunning && (
                  <span className="text-xs text-slate-500 ml-1">
                    ({procs.length})
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
