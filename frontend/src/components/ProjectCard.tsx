import type { CSSProperties } from "react";
import type { HistoryPoint, ProjectStatus } from "../types";
import { Sparkline } from "./Sparkline";
import { nombreVisible } from "../nombres";
import { Anillo } from "./Anillo";
import { estaVigente, horasDesde } from "../vigencia";

interface Props {
  project: ProjectStatus;
  history: HistoryPoint[];
  isDark: boolean;
  orden?: number;
}

export function ProjectCard({ project, history, isDark, orden = 0 }: Props) {
  const brandColor = isDark ? project.color_dark : project.color_light;

  let statusClass = "status-neutral";
  let statusLabel = "Sin datos aún";
  const vigente = estaVigente(project.checked_at);
  if (project.disponible != null && !vigente) {
    const h = horasDesde(project.checked_at);
    statusClass = "status-neutral";
    statusLabel = h != null ? `${Math.max(1, Math.round(h / 24))} d sin revisar` : "Sin revisar";
  } else if (project.disponible === true) {
    const isSlow = (project.tiempo_ms ?? 0) > 900;
    statusClass = isSlow ? "status-warning" : "status-good";
    statusLabel = isSlow ? "Lento" : "Funcionando";
  } else if (project.disponible === false) {
    statusClass = "status-warning";
    statusLabel = "No responde";
  }

  return (
    <a
      className="card"
      href={project.url}
      target="_blank"
      rel="noopener noreferrer"
      style={{ "--marca": brandColor, animationDelay: `${Math.min(orden, 12) * 45}ms` } as CSSProperties}
    >
      <div className="card-top">
        <div>
          <p className="proj-name">
            <span className="swatch" style={{ background: brandColor }} />
            {nombreVisible(project.slug, project.name)}
          </p>
        </div>
        <span className={`status-pill ${statusClass}`}>
          <span className="dot" />
          {statusLabel}
        </span>
      </div>

      <div className="metrics">
        <div className="metric">
          <div className="v">{project.tiempo_ms != null ? `${project.tiempo_ms}ms` : "—"}</div>
          <div className="k">Responde en</div>
        </div>
        <div className="metric metric-semana">
          <Anillo valor={project.uptime_pct_7d} color={brandColor} tamano={38} grosor={6} />
          <div>
            <div className="v">{project.uptime_pct_7d}%</div>
            <div className="k">Funcionando esta semana</div>
          </div>
        </div>
      </div>

      <Sparkline history={history} brandColor={brandColor} />
      <div className="spark-caption">
        <span>hace 7 días</span>
        <span>ahora</span>
      </div>
    </a>
  );
}
