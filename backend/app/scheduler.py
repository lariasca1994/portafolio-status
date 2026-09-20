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


def check_one_project(project: dict):
    start = time.perf_counter()
    status_code = None
    disponible = False
    try:
        resp = httpx.get(
            project["url"],
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
            url=project["url"],
            status_code=status_code,
            tiempo_ms=tiempo_ms,
            disponible=disponible,
        )
    except Exception:
        logger.exception("No se pudo guardar el chequeo de %s en Oracle", project["slug"])


def check_all_projects():
    for project in PROJECTS:
        check_one_project(project)


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="America/Bogota")
    scheduler.add_job(
        check_all_projects,
        "interval",
        minutes=settings.CHECK_INTERVAL_MINUTES,
        id="check_all_projects",
    )
    scheduler.start()
    return scheduler
