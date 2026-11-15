// La API entrega CHECKED_AT sin zona y en UTC. Un estado de hace más de un día no se presenta
// como "ahora": puede que el monitor no haya podido revisar ese proyecto desde entonces.
export const HORAS_VIGENCIA = 24;

export function horasDesde(checkedAt: string | null): number | null {
  if (!checkedAt) return null;
  const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(checkedAt) ? checkedAt : `${checkedAt}Z`;
  const t = Date.parse(iso);
  return Number.isFinite(t) ? (Date.now() - t) / 3_600_000 : null;
}

export function estaVigente(checkedAt: string | null): boolean {
  const h = horasDesde(checkedAt);
  return h != null && h <= HORAS_VIGENCIA;
}
