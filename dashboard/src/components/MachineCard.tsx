import { Link } from "react-router-dom";
import { Monitor, Terminal } from "lucide-react";
import type { Machine } from "@/types";
import { StatusBadge } from "./StatusBadge";

interface MachineCardProps {
  machine: Machine;
}

function MetricBar({ label, value }: { label: string; value: number }) {
  const color =
    value < 60 ? "bg-emerald-400" : value < 80 ? "bg-yellow-400" : "bg-red-400";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300">{Math.round(value)}%</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

export function MachineCard({ machine }: MachineCardProps) {
  const m = machine.latest_metrics;
  const OsIcon = machine.os_type === "windows" ? Monitor : Terminal;

  // Count running agent processes
  const agentNames = ["claude", "node", "python", "code", "cursor", "docker"];
  const runningAgents = m
    ? [...new Set(m.processes.filter((p) => agentNames.includes(p.name)).map((p) => p.name))]
    : [];

  return (
    <Link
      to={`/machines/${machine.id}`}
      className="block bg-slate-800 rounded-xl border border-slate-700 p-5 hover:border-slate-600 transition-colors no-underline"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <OsIcon className="w-5 h-5 text-slate-400" />
          <h2 className="text-base font-semibold text-white">
            {machine.machine_name}
          </h2>
        </div>
        <StatusBadge isOnline={machine.is_online} />
      </div>

      {m ? (
        <div className="space-y-3">
          <div className="space-y-2">
            <MetricBar label="CPU" value={m.cpu_percent} />
            <MetricBar label="Memory" value={m.memory_percent} />
            <MetricBar label="Disk" value={m.disk_percent} />
          </div>

          {runningAgents.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {runningAgents.map((name) => (
                <span
                  key={name}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 text-xs"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  {name}
                </span>
              ))}
            </div>
          )}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No metrics available</p>
      )}
    </Link>
  );
}
