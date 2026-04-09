import axios from "axios";
import type { HistoryResponse, Machine, TokenUsageResponse } from "@/types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  withCredentials: true, // Send cookies with requests
});

// Redirect to login on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export async function login(
  code: string,
): Promise<{ token: string; expires_in: number }> {
  const { data } = await api.post<{ token: string; expires_in: number }>(
    "/auth/login",
    { code },
  );
  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } catch {
    // ignore errors
  }
  window.location.href = "/login";
}

export async function isAuthenticated(): Promise<boolean> {
  try {
    await api.get("/auth/check");
    return true;
  } catch {
    return false;
  }
}

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

export async function fetchTokenUsage(
  id: number,
  hours: number,
): Promise<TokenUsageResponse> {
  const { data } = await api.get<TokenUsageResponse>(
    `/machines/${id}/token-usage`,
    { params: { hours } },
  );
  return data;
}
