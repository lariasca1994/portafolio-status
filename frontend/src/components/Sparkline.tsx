import type { HistoryPoint } from "../types";

interface Props {
  history: HistoryPoint[];
  brandColor: string;
}

/**
 * Barras del historial reciente. La altura refleja qué tan rápido
 * respondió en cada revisión. El color normalmente es el color propio
 * del proyecto (brandColor); si esa revisión falló o fue muy lenta
 * comparada con las demás, se pinta en ámbar/rojo para que la
 * advertencia se note incluso sobre proyectos cuyo color de marca ya
 * es cálido (como PRPagos, en rojo-naranja de Oracle).
 */
export function Sparkline({ history, brandColor }: Props) {
  if (history.length === 0) {
    return <div className="spark" />;
  }

  const times = history.map((p) => p.tiempo_ms ?? 0).filter((t) => t > 0);
  const maxMs = Math.max(...times, 1);
  const avgMs = times.length ? times.reduce((a, b) => a + b, 0) / times.length : 1;

  return (
    <div className="spark">
      {history.map((point, i) => {
        const isDown = !point.disponible;
        const isSlow = !isDown && (point.tiempo_ms ?? 0) > avgMs * 1.6;
        const height = isDown ? 18 : Math.max(15, ((point.tiempo_ms ?? 0) / maxMs) * 100);

        let background = brandColor;
        let boxShadow: string | undefined;
        if (isDown) {
          background = "var(--critical)";
        } else if (isSlow) {
          background = "var(--warning)";
          boxShadow = "0 0 0 1.5px var(--critical) inset";
        }

        return (
          <div
            key={i}
            style={{ height: `${height}%`, background, boxShadow }}
            title={isDown ? "No respondió en ese chequeo" : `${point.tiempo_ms} ms`}
          />
        );
      })}
    </div>
  );
}
