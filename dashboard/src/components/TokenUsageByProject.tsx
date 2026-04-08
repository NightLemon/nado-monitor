import { useTokenUsage } from "@/hooks/useTokenUsage";
import type { TokenUsageSummary } from "@/types";

interface TokenUsageByProjectProps {
  machineId: number;
  hours: number;
}

function formatNumber(n: number): string {
  return n.toLocaleString();
}

function projectDisplayName(path: string): string {
  // Convert "c--Users-lxiang-repos-nado-monitor" → "nado-monitor"
  const parts = path.split("-");
  // Find the last meaningful segment after "repos" or similar
  const reposIdx = parts.lastIndexOf("repos");
  if (reposIdx >= 0 && reposIdx < parts.length - 1) {
    return parts.slice(reposIdx + 1).join("-");
  }
  // Fallback: last 2 segments
  return parts.slice(-2).join("-");
}

export function TokenUsageByProject({
  machineId,
  hours,
}: TokenUsageByProjectProps) {
  const { data, isLoading } = useTokenUsage(machineId, hours);

  if (isLoading || !data || data.by_project.length === 0) return null;

  // Sort by total tokens descending
  const sorted = [...data.by_project].sort(
    (a, b) =>
      b.total_input_tokens +
      b.total_output_tokens -
      (a.total_input_tokens + a.total_output_tokens),
  );

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-4">
        Token Usage by Project
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase">
              <th className="text-left py-2 pr-4">Project</th>
              <th className="text-left py-2 pr-4">Model</th>
              <th className="text-right py-2 pr-4">Input</th>
              <th className="text-right py-2 pr-4">Output</th>
              <th className="text-right py-2 pr-4">Cache Read</th>
              <th className="text-right py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row: TokenUsageSummary, i: number) => (
              <tr
                key={`${row.project_path}-${row.model}`}
                className={i % 2 === 0 ? "bg-slate-800" : "bg-slate-800/50"}
              >
                <td className="py-2 pr-4 text-slate-200 font-medium">
                  {projectDisplayName(row.project_path)}
                </td>
                <td className="py-2 pr-4 text-slate-400 font-mono text-xs">
                  {row.model}
                </td>
                <td className="py-2 pr-4 text-right text-emerald-400">
                  {formatNumber(row.total_input_tokens)}
                </td>
                <td className="py-2 pr-4 text-right text-blue-400">
                  {formatNumber(row.total_output_tokens)}
                </td>
                <td className="py-2 pr-4 text-right text-violet-400">
                  {formatNumber(row.total_cache_read_tokens)}
                </td>
                <td className="py-2 text-right text-slate-100 font-semibold">
                  {formatNumber(
                    row.total_input_tokens + row.total_output_tokens,
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
