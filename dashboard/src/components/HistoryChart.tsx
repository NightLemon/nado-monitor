import { useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { HistoryPoint } from "@/types";
import { useMachineHistory } from "@/hooks/useMachineHistory";

interface HistoryChartProps {
  machineId: number;
}

const TIME_RANGES = [
  { label: "1h", hours: 1 },
  { label: "6h", hours: 6 },
  { label: "24h", hours: 24 },
  { label: "7d", hours: 168 },
];

function formatTime(timestamp: string, hours: number): string {
  const d = new Date(timestamp);
  if (hours <= 24) {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function HistoryChart({ machineId }: HistoryChartProps) {
  const [hours, setHours] = useState(24);
  const { data, isLoading, error } = useMachineHistory(machineId, hours);

  const chartData = useMemo(() => {
    if (!data) return [];
    return data.data_points.map((p: HistoryPoint) => ({
      ...p,
      time: formatTime(p.timestamp, hours),
    }));
  }, [data, hours]);

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
          History
        </h3>
        <div className="flex gap-1">
          {TIME_RANGES.map((r) => (
            <button
              key={r.hours}
              onClick={() => setHours(r.hours)}
              className={`px-3 py-1 text-xs rounded-md transition-colors cursor-pointer ${
                hours === r.hours
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "text-slate-400 hover:text-slate-200 border border-transparent"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center text-slate-500">
          Loading...
        </div>
      ) : error ? (
        <div className="h-64 flex items-center justify-center text-red-400">
          Failed to load history data
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-slate-500">
          No data available
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <XAxis
              dataKey="time"
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
              tickFormatter={(v: number) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                color: "#e2e8f0",
              }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="cpu_percent"
              name="CPU"
              stroke="#34d399"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="memory_percent"
              name="Memory"
              stroke="#60a5fa"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="disk_percent"
              name="Disk"
              stroke="#fbbf24"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
