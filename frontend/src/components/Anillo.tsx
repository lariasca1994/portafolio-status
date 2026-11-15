import type { ReactNode } from "react";

interface Props {
  /** Porcentaje de 0 a 100. */
  valor: number;
  color: string;
  tamano?: number;
  grosor?: number;
  children?: ReactNode;
}

/** Anillo de progreso (decorativo: la cifra va dentro o al lado como texto). */
export function Anillo({ valor, color, tamano = 52, grosor = 6, children }: Props) {
  const v = Math.max(0, Math.min(100, Number.isFinite(valor) ? valor : 0));
  const r = 50 - grosor;
  return (
    <span className="anillo" style={{ width: tamano, height: tamano }}>
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <circle className="anillo-pista" cx="50" cy="50" r={r} pathLength={100} style={{ strokeWidth: grosor * 1.6 }} />
        {v > 0 && (
          <circle
            className="anillo-avance"
            cx="50"
            cy="50"
            r={r}
            pathLength={100}
            style={{ stroke: color, strokeWidth: grosor * 1.6, strokeDashoffset: 100 - Math.max(v, 1.5) }}
          />
        )}
      </svg>
      {children && <span className="anillo-centro">{children}</span>}
    </span>
  );
}
