import { Link } from "react-router-dom";
import { Monitor, Terminal } from "lucide-react";
import type { Machine } from "@/types";
import { StatusBadge } from "./StatusBadge";
import { estimateCost, formatCost } from "@/utils/pricing";

interface MachineCardProps {
  machine: Machine;
}

function metricColor(v: number) {
  return v < 60 ? "text-emerald-400" : v < 80 ? "text-yellow-400" : "text-red-400";
}

export function MachineCard({ machine }: MachineCardProps) {
  const m = machine.latest_metrics;
  const OsIcon = machine.os_type === "windows" ? Monitor : Terminal;

  const t = machine.today_tokens;
  const todayCost =
    t.input + t.output > 0
      ? estimateCost("claude-sonnet-4", t.input, t.output, t.cache_read, t.cache_creation)
      : 0;

  const sessions = machine.session_status || [];
  const waiting = sessions.filter(
    (s) => s.status === "waiting_tool" || s.status === "waiting_input",
  );
  const running = sessions.filter((s) => s.status === "running");
  const idle = sessions.filter((s) => s.status === "idle");

  return (
    <Link
      to={`/machines/${machine.id}`}
      className="block bg-slate-800 rounded-xl border border-slate-700 p-5 hover:border-slate-600 transition-colors no-underline"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
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
          {/* Compact metrics row */}
          <div className="flex items-center gap-4 text-sm">
            <span>
              <span className="text-slate-500">CPU </span>
              <span className={`font-medium ${metricColor(m.cpu_percent)}`}>
                {Math.round(m.cpu_percent)}%
              </span>
            </span>
            <span>
              <span className="text-slate-500">MEM </span>
              <span className={`font-medium ${metricColor(m.memory_percent)}`}>
                {Math.round(m.memory_percent)}%
              </span>
            </span>
            <span>
              <span className="text-slate-500">DISK </span>
              <span className={`font-medium ${metricColor(m.disk_percent)}`}>
                {Math.round(m.disk_percent)}%
              </span>
            </span>
          </div>

          {/* Today cost */}
          {todayCost > 0 && (
            <div className="text-sm">
              <span className="text-slate-500">Today </span>
              <span className="text-amber-400 font-medium">
                {formatCost(todayCost)}
              </span>
            </div>
          )}

          {/* Session status badges */}
          {sessions.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {waiting.length > 0 && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 text-xs animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  {waiting.length} waiting
                </span>
              )}
              {running.length > 0 && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  {running.length} running
                </span>
              )}
              {idle.length > 0 && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-500/10 text-slate-400 text-xs">
                  {idle.length} idle
                </span>
              )}
            </div>
          )}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No metrics available</p>
      )}
    </Link>
  );
}
