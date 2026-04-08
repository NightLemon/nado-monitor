import { useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTokenUsage } from "@/hooks/useTokenUsage";
import { formatHourLabel } from "@/utils/time";

interface TokenUsageChartProps {
  machineId: number;
}

const TIME_RANGES = [
  { label: "1h", hours: 1 },
  { label: "6h", hours: 6 },
  { label: "24h", hours: 24 },
  { label: "7d", hours: 168 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

export function TokenUsageChart({ machineId }: TokenUsageChartProps) {
  const [hours, setHours] = useState(24);
  const { data, isLoading, error } = useTokenUsage(machineId, hours);

  const chartData = useMemo(() => {
    if (!data) return [];
    return data.by_time.map((p) => ({
      ...p,
      time: formatHourLabel(p.hour, hours),
    }));
  }, [data, hours]);

  const totalTokens = useMemo(() => {
    if (!data) return 0;
    return data.by_time.reduce(
      (sum, p) => sum + p.input_tokens + p.output_tokens,
      0,
    );
  }, [data]);

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
            Token Usage
          </h3>
          {totalTokens > 0 && (
            <p className="text-lg font-semibold text-slate-100 mt-1">
              {formatNumber(totalTokens)} tokens
            </p>
          )}
        </div>
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
          Failed to load token usage data
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-slate-500">
          No token usage data
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData}>
            <XAxis
              dataKey="time"
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
              tickFormatter={formatNumber}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                color: "#e2e8f0",
              }}
              formatter={(value) => [formatNumber(Number(value))]}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="input_tokens"
              name="Input"
              stroke="#34d399"
              fill="#34d399"
              fillOpacity={0.15}
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="output_tokens"
              name="Output"
              stroke="#60a5fa"
              fill="#60a5fa"
              fillOpacity={0.15}
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="cache_read_tokens"
              name="Cache Read"
              stroke="#a78bfa"
              fill="#a78bfa"
              fillOpacity={0.1}
              strokeWidth={1.5}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
