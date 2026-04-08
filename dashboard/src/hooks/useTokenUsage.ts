import { useQuery } from "@tanstack/react-query";
import { fetchTokenUsage } from "@/services/api";

export function useTokenUsage(machineId: number, hours: number) {
  return useQuery({
    queryKey: ["token-usage", machineId, hours],
    queryFn: () => fetchTokenUsage(machineId, hours),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}
