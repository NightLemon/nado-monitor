import { Fragment, useMemo, useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { useTokenUsage } from "@/hooks/useTokenUsage";
import { estimateCost, formatCost } from "@/utils/pricing";
import type { TokenUsageSummary } from "@/types";

interface TokenUsageByProjectProps {
  machineId: number;
  hours: number;
}

interface ProjectGroup {
  project: string;
  displayName: string;
  totalInput: number;
  totalOutput: number;
  totalCacheRead: number;
  totalCacheCreation: number;
  totalCost: number;
  models: TokenUsageSummary[];
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return n.toLocaleString();
}

function projectDisplayName(path: string): string {
  const parts = path.split("-");
  const reposIdx = parts.lastIndexOf("repos");
  if (reposIdx >= 0 && reposIdx < parts.length - 1) {
    return parts.slice(reposIdx + 1).join("-");
  }
  return parts.slice(-2).join("-");
}

export function TokenUsageByProject({
  machineId,
  hours,
}: TokenUsageByProjectProps) {
  const { data, isLoading } = useTokenUsage(machineId, hours);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const groups = useMemo<ProjectGroup[]>(() => {
    if (!data) return [];

    const map = new Map<string, ProjectGroup>();
    for (const row of data.by_project) {
      let group = map.get(row.project_path);
      if (!group) {
        group = {
          project: row.project_path,
          displayName: projectDisplayName(row.project_path),
          totalInput: 0,
          totalOutput: 0,
          totalCacheRead: 0,
          totalCacheCreation: 0,
          totalCost: 0,
          models: [],
        };
        map.set(row.project_path, group);
      }
      group.totalInput += row.total_input_tokens;
      group.totalOutput += row.total_output_tokens;
      group.totalCacheRead += row.total_cache_read_tokens;
      group.totalCacheCreation += row.total_cache_creation_tokens;
      group.totalCost += estimateCost(
        row.model,
        row.total_input_tokens,
        row.total_output_tokens,
        row.total_cache_read_tokens,
        row.total_cache_creation_tokens,
      );
      group.models.push(row);
    }

    return [...map.values()].sort(
      (a, b) =>
        b.totalInput + b.totalOutput - (a.totalInput + a.totalOutput),
    );
  }, [data]);

  if (isLoading || groups.length === 0) return null;

  function toggle(project: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(project)) next.delete(project);
      else next.add(project);
      return next;
    });
  }

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-4">
        Token Usage by Project
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase">
              <th className="text-left py-2 pr-4 w-8"></th>
              <th className="text-left py-2 pr-4">Project</th>
              <th className="text-right py-2 pr-4">Input</th>
              <th className="text-right py-2 pr-4">Output</th>
              <th className="text-right py-2 pr-4">Cache Read</th>
              <th className="text-right py-2 pr-4">Total</th>
              <th className="text-right py-2">Cost</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((group) => {
              const isOpen = expanded.has(group.project);
              const hasMultipleModels = group.models.length > 1;
              return (
                <Fragment key={group.project}>
                  <tr
                    className={`border-t border-slate-700/50 ${
                      hasMultipleModels
                        ? "cursor-pointer hover:bg-slate-700/30"
                        : ""
                    }`}
                    onClick={() => hasMultipleModels && toggle(group.project)}
                  >
                    <td className="py-2.5 pr-1 text-slate-500">
                      {hasMultipleModels &&
                        (isOpen ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        ))}
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className="text-slate-100 font-medium">
                        {group.displayName}
                      </span>
                      {!hasMultipleModels && (
                        <span className="ml-2 text-xs text-slate-500 font-mono">
                          {group.models[0].model}
                        </span>
                      )}
                      {hasMultipleModels && (
                        <span className="ml-2 text-xs text-slate-500">
                          {group.models.length} models
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 pr-4 text-right text-emerald-400 font-medium">
                      {formatNumber(group.totalInput)}
                    </td>
                    <td className="py-2.5 pr-4 text-right text-blue-400 font-medium">
                      {formatNumber(group.totalOutput)}
                    </td>
                    <td className="py-2.5 pr-4 text-right text-violet-400 font-medium">
                      {formatNumber(group.totalCacheRead)}
                    </td>
                    <td className="py-2.5 pr-4 text-right text-slate-100 font-semibold">
                      {formatNumber(group.totalInput + group.totalOutput)}
                    </td>
                    <td className="py-2.5 text-right text-amber-400 font-semibold">
                      {formatCost(group.totalCost)}
                    </td>
                  </tr>
                  {isOpen &&
                    [...group.models]
                      .sort(
                        (a, b) =>
                          b.total_input_tokens +
                          b.total_output_tokens -
                          (a.total_input_tokens + a.total_output_tokens),
                      )
                      .map((m) => (
                        <tr
                          key={`${group.project}-${m.model}`}
                          className="bg-slate-900/40"
                        >
                          <td></td>
                          <td className="py-1.5 pr-4 pl-4 text-xs text-slate-400 font-mono">
                            {m.model}
                          </td>
                          <td className="py-1.5 pr-4 text-right text-xs text-emerald-400/70">
                            {formatNumber(m.total_input_tokens)}
                          </td>
                          <td className="py-1.5 pr-4 text-right text-xs text-blue-400/70">
                            {formatNumber(m.total_output_tokens)}
                          </td>
                          <td className="py-1.5 pr-4 text-right text-xs text-violet-400/70">
                            {formatNumber(m.total_cache_read_tokens)}
                          </td>
                          <td className="py-1.5 pr-4 text-right text-xs text-slate-300">
                            {formatNumber(
                              m.total_input_tokens + m.total_output_tokens,
                            )}
                          </td>
                          <td className="py-1.5 text-right text-xs text-amber-400/70">
                            {formatCost(
                              estimateCost(
                                m.model,
                                m.total_input_tokens,
                                m.total_output_tokens,
                                m.total_cache_read_tokens,
                                m.total_cache_creation_tokens,
                              ),
                            )}
                          </td>
                        </tr>
                      ))}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
