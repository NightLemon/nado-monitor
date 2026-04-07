import { useQuery } from "@tanstack/react-query";
import { fetchMachine, fetchHistory } from "@/services/api";

export function useMachineDetail(id: number) {
  return useQuery({
    queryKey: ["machine", id],
    queryFn: () => fetchMachine(id),
    refetchInterval: 10_000,
    staleTime: 5_000,
  });
}

export function useMachineHistory(id: number, hours: number) {
  return useQuery({
    queryKey: ["machine-history", id, hours],
    queryFn: () => fetchHistory(id, hours),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}
