import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Monitor, Terminal, Loader2, AlertCircle } from "lucide-react";
import { useMachineDetail } from "@/hooks/useMachineHistory";
import { StatusBadge } from "@/components/StatusBadge";
import { MetricGauge } from "@/components/MetricGauge";
import { ProcessList } from "@/components/ProcessList";
import { HistoryChart } from "@/components/HistoryChart";

export function MachineDetailPage() {
  const { id } = useParams<{ id: string }>();
  const machineId = Number(id);
  const { data: machine, isLoading, error } = useMachineDetail(machineId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  if (error || !machine) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400 gap-2">
        <AlertCircle className="w-5 h-5" />
        <span>Machine not found</span>
      </div>
    );
  }

  const m = machine.latest_metrics;
  const OsIcon = machine.os_type === "windows" ? Monitor : Terminal;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/"
          className="p-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex items-center gap-3">
          <OsIcon className="w-6 h-6 text-slate-400" />
          <h1 className="text-2xl font-bold text-white">{machine.machine_name}</h1>
          <StatusBadge isOnline={machine.is_online} />
        </div>
      </div>

      <div className="text-sm text-slate-500">
        Last heartbeat:{" "}
        {new Date(machine.last_heartbeat).toLocaleString()}
        {" | "}
        First seen:{" "}
        {new Date(machine.first_seen).toLocaleString()}
      </div>

      {m ? (
        <>
          {/* Metric Gauges */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <div className="flex justify-around">
              <MetricGauge
                label="CPU"
                value={m.cpu_percent}
              />
              <MetricGauge
                label="Memory"
                value={m.memory_percent}
                detail={`${m.memory_used_gb} / ${m.memory_total_gb} GB`}
              />
              <MetricGauge
                label="Disk"
                value={m.disk_percent}
                detail={`${m.disk_used_gb} / ${m.disk_total_gb} GB`}
              />
            </div>
          </div>

          {/* Process List */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <ProcessList processes={m.processes} />
          </div>

          {/* History Chart */}
          <HistoryChart machineId={machineId} />
        </>
      ) : (
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 text-center text-slate-500">
          No metrics available yet
        </div>
      )}
    </div>
  );
}
