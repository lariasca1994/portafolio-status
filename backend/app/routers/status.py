from fastapi import APIRouter, HTTPException

from .. import database
from ..badges import insignia
from ..projects import PROJECTS, PROJECTS_BY_SLUG

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("")
def get_status():
    """Estado actual de todos los proyectos: el último chequeo de cada
    uno, más su % de disponibilidad y tiempo de respuesta promedio de
    los últimos 7 días. Esto es lo que pinta cada tarjeta del dashboard."""

    latest_by_slug = {row["proyecto"]: row for row in database.fetch_latest_per_project()}

    result = []
    for project in PROJECTS:
        slug = project["slug"]
        latest = latest_by_slug.get(slug)
        stats = database.fetch_uptime_percent(slug, dias=7)

        result.append(
            {
                "slug": slug,
                "name": project["name"],
                "url": project["url"],
                "color_light": project["color_light"],
                "color_dark": project["color_dark"],
                "disponible": bool(latest["disponible"]) if latest else None,
                "status_code": latest["status_code"] if latest else None,
                "tiempo_ms": latest["tiempo_ms"] if latest else None,
                "checked_at": latest["checked_at"].isoformat() if latest else None,
                "uptime_pct_7d": stats["uptime_pct"],
                "avg_ms_7d": stats["avg_ms"],
            }
        )

    return {"projects": result}


@router.get("/{slug}/historial")
def get_history(slug: str, puntos: int = 14):
    if slug not in PROJECTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    history = database.fetch_history(slug, puntos=puntos)
    return {
        "slug": slug,
        "historial": [
            {
                "disponible": bool(row["disponible"]),
                "tiempo_ms": row["tiempo_ms"],
                "checked_at": row["checked_at"].isoformat(),
            }
            for row in history
        ],
    }
import time
from datetime import datetime, timedelta, timezone

import httpx

from fastapi import APIRouter, HTTPException, Response

from .. import database
from ..badges import insignia
from ..projects import PROJECTS, PROJECTS_BY_SLUG

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("")
def get_status():
    """Estado actual de todos los proyectos: el último chequeo de cada
    uno, más su % de disponibilidad y tiempo de respuesta promedio de
    los últimos 7 días. Esto es lo que pinta cada tarjeta del dashboard."""

    latest_by_slug = {row["proyecto"]: row for row in database.fetch_latest_per_project()}

    result = []
    for project in PROJECTS:
        slug = project["slug"]
        latest = latest_by_slug.get(slug)
        stats = database.fetch_uptime_percent(slug, dias=7)

        result.append(
            {
                "slug": slug,
                "name": project["name"],
                "url": project["url"],
                "color_light": project["color_light"],
                "color_dark": project["color_dark"],
                "disponible": bool(latest["disponible"]) if latest else None,
                "status_code": latest["status_code"] if latest else None,
                "tiempo_ms": latest["tiempo_ms"] if latest else None,
                "checked_at": latest["checked_at"].isoformat() if latest else None,
                "uptime_pct_7d": stats["uptime_pct"],
                "avg_ms_7d": stats["avg_ms"],
            }
        )

    return {"projects": result}


@router.get("/{slug}/historial")
def get_history(slug: str, puntos: int = 14):
    if slug not in PROJECTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    history = database.fetch_history(slug, puntos=puntos)
    return {
        "slug": slug,
        "historial": [
            {
                "disponible": bool(row["disponible"]),
                "tiempo_ms": row["tiempo_ms"],
                "checked_at": row["checked_at"].isoformat(),
            }
            for row in history
        ],
    }


@router.get("/badge.svg")
def get_badge():
    """SVG con el resumen en vivo (cuántos proyectos están arriba ahora
    mismo y hace cuánto se revisó), pensado para incrustarse con <img>
    en un README de GitHub -- ahí no se permiten iframes ni JavaScript,
    así que esta es la forma de que al menos el conteo se vea real cada
    vez que alguien abre el perfil."""

    latest_by_slug = {row["proyecto"]: row for row in database.fetch_latest_per_project()}
    total = len(PROJECTS)
    online = sum(1 for row in latest_by_slug.values() if row["disponible"])

    ultima = None
    for row in latest_by_slug.values():
        checked = row["checked_at"]
        if ultima is None or checked > ultima:
            ultima = checked

    if ultima:
        segundos = int((datetime.now(timezone.utc) - ultima.replace(tzinfo=timezone.utc)).total_seconds())
        if segundos < 60:
            hace = f"hace {segundos} s"
        elif segundos < 3600:
            hace = f"hace {segundos // 60} min"
        else:
            hace = f"hace {segundos // 3600} h"
    else:
        hace = "sin datos aún"

    todo_bien = online == total
    color = "#3FB950" if todo_bien else "#D29922"
    svg = insignia(f"{online}/{total} proyectos en línea", f"revisado {hace}", color)

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache, max-age=60"},
    )


QA_EVIDENCIA_API = "https://ta8qn3lx78.execute-api.us-east-1.amazonaws.com/resultados"
BOGOTA = timezone(timedelta(hours=-5))  # Colombia no tiene horario de verano
_qa_cache: dict = {"hasta": 0.0, "datos": None}

# En qa-evidencia algunos proyectos usan un id distinto al slug de este monitor.
QA_ID_POR_SLUG = {"gestor-incidentes-ti": "gestorincidentesti"}


def _svg(svg: str) -> Response:
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "no-cache, max-age=60"})


def _resultados_qa() -> list[dict] | None:
    """Resultados de la última corrida de qa-evidencia (cacheados 5 min)."""
    if _qa_cache["datos"] is not None and time.time() < _qa_cache["hasta"]:
        return _qa_cache["datos"]
    try:
        datos = httpx.get(QA_EVIDENCIA_API, timeout=5).json()["resultados"]
        _qa_cache.update(hasta=time.time() + 300, datos=datos)
    except Exception:
        pass
    return _qa_cache["datos"]


def _fecha_bogota(iso: str) -> str:
    fecha = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return fecha.astimezone(BOGOTA).strftime("%d/%m/%Y · %H:%M")


def _paso(r: dict) -> bool:
    return r.get("estadoPositivo") == "paso" and r.get("estadoNegativo") == "paso"


@router.get("/qa-badge.svg")
def get_qa_badge():
    """Insignia con la fecha y hora (Bogotá, 24 h) de la última corrida de
    pruebas E2E de qa-evidencia y cuántos proyectos pasaron."""

    datos = _resultados_qa()
    if not datos:
        return _svg(insignia("Pruebas E2E", "sin datos por ahora", "#6E7681", icono="check", animado=False))
    ultima = max(datos, key=lambda r: r["fechaCorrida"])["fechaCorrida"]
    pasaron = sum(1 for r in datos if _paso(r))
    color = "#58A6FF" if pasaron == len(datos) else "#D29922"
    return _svg(insignia(f"Última prueba E2E · {_fecha_bogota(ultima)}", f"{pasaron}/{len(datos)} pasaron",
                         color, icono="check", animado=False))


@router.get("/{slug}/badge.svg")
def get_project_badge(slug: str):
    """Estado en vivo de un proyecto (para el README de su repositorio):
    en línea o caído, tiempo de respuesta y disponibilidad de 7 días."""

    if slug not in PROJECTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    latest = next((row for row in database.fetch_latest_per_project() if row["proyecto"] == slug), None)
    stats = database.fetch_uptime_percent(slug, dias=7)
    uptime = f"{stats['uptime_pct']:.1f}% disponible (7 días)" if stats["uptime_pct"] is not None else "sin historial aún"

    if latest is None:
        svg = insignia("Estado en vivo", "sin datos aún", "#6E7681", animado=False)
    elif latest["disponible"]:
        svg = insignia(f"En línea · {latest['tiempo_ms']} ms", uptime, "#3FB950")
    else:
        svg = insignia("Fuera de línea", uptime, "#F85149")
    return _svg(svg)


@router.get("/{slug}/qa-badge.svg")
def get_project_qa_badge(slug: str):
    """Fecha y hora (Bogotá, 24 h) de la última prueba E2E de un proyecto y si pasó."""

    if slug not in PROJECTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    qa_id = QA_ID_POR_SLUG.get(slug, slug)
    r = next((r for r in (_resultados_qa() or []) if r["proyecto"] == qa_id), None)
    if r is None:
        svg = insignia("Pruebas E2E", "sin corrida reciente", "#6E7681", icono="check", animado=False)
    elif _paso(r):
        svg = insignia(f"Prueba E2E · {_fecha_bogota(r['fechaCorrida'])}", "pasó", "#58A6FF", icono="check", animado=False)
    else:
        svg = insignia(f"Prueba E2E · {_fecha_bogota(r['fechaCorrida'])}", "falló", "#F85149", icono="check", animado=False)
    return _svg(svg)
