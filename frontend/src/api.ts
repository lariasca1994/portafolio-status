import type { HistoryResponse, StatusResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchStatus(): Promise<StatusResponse> {
  const res = await fetch(`${API_URL}/api/status`);
  if (!res.ok) throw new Error("No se pudo cargar el estado de los proyectos");
  return res.json();
}

export async function fetchHistory(slug: string, puntos = 14): Promise<HistoryResponse> {
  const res = await fetch(`${API_URL}/api/status/${slug}/historial?puntos=${puntos}`);
  if (!res.ok) throw new Error(`No se pudo cargar el historial de ${slug}`);
  return res.json();
}
