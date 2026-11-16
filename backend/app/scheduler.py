"""
Cada CHECK_INTERVAL_MINUTES minutos, le hace un GET a cada proyecto y
guarda el resultado en Oracle: si respondió bien, con qué código HTTP,
y cuántos milisegundos se demoró.
"""

import time
import logging
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings
from .database import delete_old_checks, fetch_latest_per_project, insert_check
from .projects import PROJECTS

logger = logging.getLogger("portfolio-status.scheduler")

BOGOTA = ZoneInfo("America/Bogota")
_PONIENDO_AL_DIA = threading.Lock()


# Tiempo para que un servicio dormido arranque (contenedor en frío, Render, base que se reanuda).
TIMEOUT_DESPERTAR_SEGUNDOS = 90.0


def _despertar(url: str) -> None:
    """Petición previa que no se registra: así la medición no cuenta el arranque en frío
    (ni lo marca como caído por tardar), y las estadísticas reflejan el servicio despierto."""
    try:
        httpx.get(url, timeout=TIMEOUT_DESPERTAR_SEGUNDOS, follow_redirects=True)
    except httpx.RequestError:
        pass


def check_one_project(project: dict):
    url = project.get("check_url", project["url"])
    if project.get("revisar_horas"):
        _despertar(url)
    start = time.perf_counter()
    status_code = None
    disponible = False
    try:
        resp = httpx.get(
            url,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        status_code = resp.status_code
        disponible = resp.status_code < 500
    except httpx.RequestError as exc:
        logger.warning("Fallo revisando %s: %s", project["slug"], exc)

    tiempo_ms = round((time.perf_counter() - start) * 1000)

    try:
        insert_check(
            proyecto=project["slug"],
            url=url,
            status_code=status_code,
            tiempo_ms=tiempo_ms,
            disponible=disponible,
        )
    except Exception:
        logger.exception("No se pudo guardar el chequeo de %s en Oracle", project["slug"])


def check_all_projects():
    """Proyectos que se revisan cada pocos minutos (sin "revisar_horas"); al final se ponen al
    día los de horas fijas que se hayan quedado sin revisar."""
    for project in PROJECTS:
        if not project.get("revisar_horas"):
            check_one_project(project)
    check_pendientes()


def ultima_franja(horas: list[int], ahora: datetime) -> datetime:
    """La hora fija más reciente (de hoy o de ayer, en Bogotá) que ya pasó."""
    candidatos = [
        (ahora - timedelta(days=dias)).replace(hour=hora, minute=0, second=0, microsecond=0)
        for dias in (0, 1) for hora in horas
    ]
    return max(c for c in candidatos if c <= ahora)


def _en_bogota(momento: datetime) -> datetime:
    """CHECKED_AT llega sin zona y está en UTC (zona de la base)."""
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(BOGOTA)


def check_pendientes(ahora: datetime | None = None, ultimos: dict | None = None) -> list[str]:
    """Render duerme este servicio cuando no hay tráfico, y el cron de horas fijas no corre si en
    ese momento está dormido: sin esto, esos proyectos se quedaban días sin revisar (y el tablero
    mostraba un estado viejo y 0 % en la semana). Cada vez que el servicio está despierto se revisa,
    una sola vez, cada proyecto cuya última revisión es anterior a su franja más reciente."""
    if not _PONIENDO_AL_DIA.acquire(blocking=False):
        return []
    revisados = []
    try:
        ahora = ahora or datetime.now(BOGOTA)
        if ultimos is None:
            try:
                ultimos = {fila["proyecto"]: fila["checked_at"] for fila in fetch_latest_per_project()}
            except Exception:
                logger.exception("No se pudo leer la última revisión de cada proyecto")
                return []
        for project in PROJECTS:
            horas = project.get("revisar_horas")
            if not horas:
                continue
            ultimo = ultimos.get(project["slug"])
            if ultimo is None or _en_bogota(ultimo) < ultima_franja(horas, ahora):
                logger.info("Revisión pendiente de %s (última: %s)", project["slug"], ultimo)
                check_one_project(project)
                revisados.append(project["slug"])
    finally:
        _PONIENDO_AL_DIA.release()
    return revisados


def check_scheduled_projects(hora: int):
    """Proyectos con "revisar_horas": solo a esas horas, para que puedan dormir."""
    for project in PROJECTS:
        if hora in project.get("revisar_horas", []):
            check_one_project(project)


def depurar_chequeos():
    """Una vez al día borra los chequeos con más de 15 días."""
    try:
        borrados = delete_old_checks(15)
        logger.info("Depuración: %s chequeos con más de 15 días borrados", borrados)
    except Exception:  # noqa: BLE001 - la depuración nunca debe tumbar el servicio
        logger.exception("No se pudo depurar CHECKS_LOG")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="America/Bogota")
    scheduler.add_job(
        check_all_projects,
        "interval",
        minutes=settings.CHECK_INTERVAL_MINUTES,
        id="check_all_projects",
    )
    horas = sorted({h for p in PROJECTS for h in p.get("revisar_horas", [])})
    for hora in horas:
        scheduler.add_job(
            check_scheduled_projects,
            "cron",
            hour=hora,
            minute=0,
            args=[hora],
            id=f"check_scheduled_{hora}",
        )
    scheduler.add_job(depurar_chequeos, "cron", hour=3, minute=15, id="depurar_chequeos")
    scheduler.start()
    return scheduler
