import type { HistoryResponse, StatusResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/** La API no responde (Render caído) o la base Oracle no está disponible (503). */
export class MantenimientoError extends Error {}

const ESTADOS_MANTENIMIENTO = [502, 503, 504];

async function pedir(ruta: string): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${ruta}`);
  } catch {
    throw new MantenimientoError("La API no responde");
  }
  if (ESTADOS_MANTENIMIENTO.includes(res.status)) throw new MantenimientoError(`La API respondió ${res.status}`);
  return res;
}

export async function fetchStatus(): Promise<StatusResponse> {
  const res = await pedir("/api/status");
  if (!res.ok) throw new Error("No se pudo cargar el estado de los proyectos");
  return res.json();
}

export async function fetchHistory(slug: string, puntos = 14): Promise<HistoryResponse> {
  const res = await pedir(`/api/status/${slug}/historial?puntos=${puntos}`);
  if (!res.ok) throw new Error(`No se pudo cargar el historial de ${slug}`);
  return res.json();
}
