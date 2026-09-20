import { useEffect, useState } from "react";
import { fetchHistory, fetchStatus } from "./api";
import type { HistoryPoint, ProjectStatus } from "./types";
import { ProjectCard } from "./components/ProjectCard";

const REFRESH_MS = 60_000;

function useIsDark(): boolean {
  const [isDark, setIsDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches
  );
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setIsDark(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return isDark;
}

export default function App() {
  const [projects, setProjects] = useState<ProjectStatus[]>([]);
  const [histories, setHistories] = useState<Record<string, HistoryPoint[]>>({});
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [theme, setTheme] = useState<"light" | "dark" | null>(null);
  const systemIsDark = useIsDark();
  const isDark = theme ? theme === "dark" : systemIsDark;

  async function load() {
    const status = await fetchStatus();
    setProjects(status.projects);
    setLastUpdated(new Date());

    const entries = await Promise.all(
      status.projects.map(async (p) => {
        const h = await fetchHistory(p.slug);
        return [p.slug, h.historial] as const;
      })
    );
    setHistories(Object.fromEntries(entries));
  }

  useEffect(() => {
    load().catch(console.error);
    const id = setInterval(() => load().catch(console.error), REFRESH_MS);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
  }, [isDark]);

  const online = projects.filter((p) => p.disponible).length;

  return (
    <div className="wrap">
      <header>
        <div>
          <p className="eyebrow">Portafolio de Luis Felipe Arias</p>
          <h1>Estado de mis proyectos</h1>
          <p className="sub">
            Panel de monitoreo en tiempo real: cada pocos minutos se valida si cada proyecto del
            portafolio sigue disponible y cuánto tarda en responder. Haz clic en cualquier tarjeta
            para abrir el proyecto en vivo.
          </p>
        </div>
        <button
          className="theme-toggle"
          type="button"
          onClick={() => setTheme(isDark ? "light" : "dark")}
        >
          🌓 {isDark ? "Oscuro" : "Claro"}
        </button>
      </header>

      <div className="explainer">
        <b>¿Qué son estos números?</b> "Responde en" es cuánto se demora la página en cargar
        cuando alguien entra — entre menos, mejor. "Funcionando esta semana" es el porcentaje de
        las veces que, al revisarlo, el proyecto respondió correctamente. El punto de color junto
        al nombre muestra el estado justo ahora: <span style={{ color: "var(--good)", fontWeight: 600 }}>verde = funcionando</span>,{" "}
        <span style={{ color: "#9a6b00", fontWeight: 600 }}>ámbar = responde lento o no responde</span>.
        El color de la barra de abajo es simplemente el color de cada proyecto — no tiene que ver
        con si algo anda mal.
      </div>

      <div className="summary">
        <div>
          <span className="figure">{online}</span>
          <small>de {projects.length || "…"} proyectos funcionando ahora</small>
        </div>
        <div className="label">
          {lastUpdated ? `· última revisión hace ${Math.round((Date.now() - lastUpdated.getTime()) / 1000)}s` : ""}
        </div>
      </div>

      <div className="grid">
        {projects.map((p) => (
          <ProjectCard key={p.slug} project={p} history={histories[p.slug] ?? []} isDark={isDark} />
        ))}
      </div>

      <footer className="stack-footer">
        <span className="stack-dot" />
        Construido con <b>FastAPI</b> y <b>React</b> · historial de disponibilidad persistido en{" "}
        <b>Oracle Autonomous Database</b>
      </footer>
    </div>
  );
}