export interface ProcessInfo {
  name: string;
  pid: number;
  process_name: string;
  status: string;
}

export interface LatestMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  processes: ProcessInfo[];
  timestamp: string;
}

export interface Machine {
  id: number;
  machine_name: string;
  os_type: "windows" | "linux";
  is_online: boolean;
  last_heartbeat: string;
  first_seen: string;
  latest_metrics: LatestMetrics | null;
}

export interface HistoryPoint {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

export interface HistoryResponse {
  machine_name: string;
  data_points: HistoryPoint[];
}
