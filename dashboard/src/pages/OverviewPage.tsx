import { useMachines } from "@/hooks/useMachines";
import { MachineCard } from "@/components/MachineCard";
import { AlertCircle, Loader2 } from "lucide-react";

export function OverviewPage() {
  const { data: machines, isLoading, error } = useMachines();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400 gap-2">
        <AlertCircle className="w-5 h-5" />
        <span>Failed to load machines</span>
      </div>
    );
  }

  if (!machines || machines.length === 0) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold text-slate-300 mb-2">
          No machines registered
        </h2>
        <p className="text-slate-500">
          Start a telemetry client on your machines to see them here.
        </p>
      </div>
    );
  }

  const online = machines.filter((m) => m.is_online).length;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Machines</h1>
        <span className="text-sm text-slate-400">
          {online}/{machines.length} online
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {machines.map((machine) => (
          <MachineCard key={machine.id} machine={machine} />
        ))}
      </div>
    </div>
  );
}
