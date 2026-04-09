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

export interface SessionStatus {
  project_path: string;
  session_id: string;
  status: "running" | "waiting_tool" | "waiting_input" | "idle";
  model: string;
  last_activity: string;
  slug: string;
}

export interface TodayTokens {
  input: number;
  output: number;
  cache_read: number;
  cache_creation: number;
}

export interface Machine {
  id: number;
  machine_name: string;
  os_type: "windows" | "linux";
  is_online: boolean;
  last_heartbeat: string;
  first_seen: string;
  latest_metrics: LatestMetrics | null;
  session_status: SessionStatus[];
  today_tokens: TodayTokens;
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

export interface TokenUsageSummary {
  project_path: string;
  model: string;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
}

export interface TokenUsageTimePoint {
  hour: string;
  input_tokens: number;
  output_tokens: number;
  cache_creation_tokens: number;
  cache_read_tokens: number;
}

export interface TokenUsageResponse {
  machine_name: string;
  by_project: TokenUsageSummary[];
  by_time: TokenUsageTimePoint[];
}
