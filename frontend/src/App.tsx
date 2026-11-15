import { useEffect, useState } from "react";
import { fetchHistory, fetchStatus, MantenimientoError } from "./api";
import type { HistoryPoint, ProjectStatus } from "./types";
import { ProjectCard } from "./components/ProjectCard";
import { Anillo } from "./components/Anillo";
import { estaVigente } from "./vigencia";

const REFRESH_MS = 60_000;
// En mantenimiento se reintenta más seguido; con la primera respuesta buena vuelve el tablero.
const REINTENTO_MANTENIMIENTO_MS = 15_000;

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
  const [enMantenimiento, setEnMantenimiento] = useState(false);

  async function load() {
    const status = await fetchStatus();
    setProjects(status.projects);
    setLastUpdated(new Date());
    setEnMantenimiento(false);

    const entries = await Promise.all(
      status.projects.map(async (p) => {
        const h = await fetchHistory(p.slug);
        return [p.slug, h.historial] as const;
      })
    );
    setHistories(Object.fromEntries(entries));
  }

  function cargar() {
    load().catch((error) => {
      if (error instanceof MantenimientoError) setEnMantenimiento(true);
      else console.error(error);
    });
  }

  useEffect(() => {
    cargar();
    const id = setInterval(cargar, enMantenimiento ? REINTENTO_MANTENIMIENTO_MS : REFRESH_MS);
    return () => clearInterval(id);
  }, [enMantenimiento]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
  }, [isDark]);

  // Solo cuenta como "ahora" lo revisado en las últimas 24 horas.
  const vigentes = projects.filter((p) => p.disponible != null && estaVigente(p.checked_at));
  const online = vigentes.filter((p) => p.disponible).length;
  const conDatos = vigentes;
  const tiempos = projects.filter((p) => p.disponible && p.tiempo_ms != null).map((p) => p.tiempo_ms as number);
  const promedioMs = tiempos.length ? Math.round(tiempos.reduce((a, b) => a + b, 0) / tiempos.length) : null;
  const semanal = projects.length ? projects.reduce((a, p) => a + (p.uptime_pct_7d || 0), 0) / projects.length : 0;
  const pctAhora = conDatos.length ? (online / conDatos.length) * 100 : 0;
  // Cuenta regresiva del próximo intento mientras la API está en mantenimiento.
  const [resto, setResto] = useState(REINTENTO_MANTENIMIENTO_MS / 1000);
  useEffect(() => {
    if (!enMantenimiento) return;
    setResto(REINTENTO_MANTENIMIENTO_MS / 1000);
    const id = setInterval(() => setResto((r) => (r <= 1 ? REINTENTO_MANTENIMIENTO_MS / 1000 : r - 1)), 1000);
    return () => clearInterval(id);
  }, [enMantenimiento]);

  return (
    <div className="wrap">
      <header>
        <div>
          <p className="eyebrow">Portafolio de Luis Felipe Arias</p>
          <h1>Monitor de disponibilidad de servicios</h1>
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

      {enMantenimiento ? (
        <section className="mantenimiento" role="status" aria-live="polite">
          <div className="mantenimiento-icono" aria-hidden="true"><span /><span /><span /></div>
          <p className="eyebrow">Monitor de disponibilidad de servicios</p>
          <h2>Estamos en mantenimiento</h2>
          <p className="sub">
            El servicio de monitoreo no está respondiendo en este momento, así que no se puede mostrar el estado
            de los proyectos.
          </p>
          <ul>
            <li>El historial de disponibilidad sigue guardado.</li>
            <li>Los proyectos del portafolio no dependen de este panel: pueden estar funcionando con normalidad.</li>
            <li>El panel vuelve solo apenas el servicio responda.</li>
          </ul>
          <p className="reintento">
            <Anillo valor={(resto / (REINTENTO_MANTENIMIENTO_MS / 1000)) * 100} color="var(--oracle)" tamano={20} grosor={5} />
            <span>Nuevo intento en {resto} s</span>
          </p>
        </section>
      ) : (
      <>
      {/* Tarjeta protagonista (estilo Helios/Dwisun): estado de ahora con anillo y dos cifras de la semana. */}
      <section className="summary heroe" aria-label="Resumen del portafolio">
        <div className="heroe-principal">
          <Anillo valor={pctAhora} color="#ffffff" tamano={88} grosor={7}>
            <b>{Math.round(pctAhora)}%</b>
          </Anillo>
          <div>
            <p className="heroe-etiqueta"><span className="pulso" aria-hidden="true" /> En vivo</p>
            <span className="figure">{online}</span>
            <small>de {projects.length || "…"} proyectos funcionando ahora</small>
            {projects.length > 0 && vigentes.length < projects.length && (
              <div className="label">{projects.length - vigentes.length} sin revisión en las últimas 24 h</div>
            )}
            <div className="label">
              {lastUpdated ? `Última revisión hace ${Math.round((Date.now() - lastUpdated.getTime()) / 1000)}s` : "Cargando…"}
            </div>
          </div>
        </div>
        <div className="heroe-cifras">
          <div>
            <span>{promedioMs != null ? `${promedioMs} ms` : "—"}</span>
            <small>respuesta promedio ahora</small>
          </div>
          <div>
            <span>{projects.length ? `${semanal.toFixed(1)}%` : "—"}</span>
            <small>funcionando esta semana (promedio)</small>
          </div>
        </div>
      </section>

      <div className="grid">
        {projects.map((p, i) => (
          <ProjectCard key={p.slug} project={p} history={histories[p.slug] ?? []} isDark={isDark} orden={i} />
        ))}
      </div>
      </>
      )}

      <footer className="stack-footer">
        <span className="stack-dot" />
        Construido con <b>FastAPI</b> y <b>React</b> · historial de disponibilidad persistido en{" "}
        <b>Oracle Autonomous Database</b>
      </footer>
    </div>
  );
}