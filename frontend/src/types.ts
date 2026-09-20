export interface ProjectStatus {
  slug: string;
  name: string;
  url: string;
  color_light: string;
  color_dark: string;
  disponible: boolean | null;
  status_code: number | null;
  tiempo_ms: number | null;
  checked_at: string | null;
  uptime_pct_7d: number;
  avg_ms_7d: number;
}

export interface StatusResponse {
  projects: ProjectStatus[];
}

export interface HistoryPoint {
  disponible: boolean;
  tiempo_ms: number | null;
  checked_at: string;
}

export interface HistoryResponse {
  slug: string;
  historial: HistoryPoint[];
}
