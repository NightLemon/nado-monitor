import { useQuery } from "@tanstack/react-query";
import { fetchMachines } from "@/services/api";

export function useMachines() {
  return useQuery({
    queryKey: ["machines"],
    queryFn: fetchMachines,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });
}
