import type { HistoryPoint, ProjectStatus } from "../types";
import { Sparkline } from "./Sparkline";

interface Props {
  project: ProjectStatus;
  history: HistoryPoint[];
  isDark: boolean;
}

export function ProjectCard({ project, history, isDark }: Props) {
  const brandColor = isDark ? project.color_dark : project.color_light;

  let statusClass = "status-neutral";
  let statusLabel = "Sin datos aún";
  if (project.disponible === true) {
    const isSlow = (project.tiempo_ms ?? 0) > 900;
    statusClass = isSlow ? "status-warning" : "status-good";
    statusLabel = isSlow ? "Lento" : "Funcionando";
  } else if (project.disponible === false) {
    statusClass = "status-warning";
    statusLabel = "No responde";
  }

  return (
    <a className="card" href={project.url} target="_blank" rel="noopener noreferrer">
      <div className="card-top">
        <div>
          <p className="proj-name">
            <span className="swatch" style={{ background: brandColor }} />
            {project.name}
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
        <div className="metric">
          <div className="v">{project.uptime_pct_7d}%</div>
          <div className="k">Funcionando esta semana</div>
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
