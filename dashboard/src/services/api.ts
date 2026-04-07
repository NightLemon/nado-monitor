import axios from "axios";
import type { HistoryResponse, Machine } from "@/types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
});

export async function fetchMachines(): Promise<Machine[]> {
  const { data } = await api.get<Machine[]>("/machines");
  return data;
}

export async function fetchMachine(id: number): Promise<Machine> {
  const { data } = await api.get<Machine>(`/machines/${id}`);
  return data;
}

export async function fetchHistory(
  id: number,
  hours: number,
): Promise<HistoryResponse> {
  const { data } = await api.get<HistoryResponse>(
    `/machines/${id}/history`,
    { params: { hours } },
  );
  return data;
}
