"""
Cada CHECK_INTERVAL_MINUTES minutos, le hace un GET a cada proyecto y
guarda el resultado en Oracle: si respondió bien, con qué código HTTP,
y cuántos milisegundos se demoró.
"""

import time
import logging

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings
from .database import insert_check
from .projects import PROJECTS

logger = logging.getLogger("portfolio-status.scheduler")


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
    """Proyectos que se revisan cada pocos minutos (sin "revisar_horas")."""
    for project in PROJECTS:
        if not project.get("revisar_horas"):
            check_one_project(project)


def check_scheduled_projects(hora: int):
    """Proyectos con "revisar_horas": solo a esas horas, para que puedan dormir."""
    for project in PROJECTS:
        if hora in project.get("revisar_horas", []):
            check_one_project(project)


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
    scheduler.start()
    return scheduler
