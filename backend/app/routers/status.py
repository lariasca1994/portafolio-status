from fastapi import APIRouter, HTTPException

from .. import database
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
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response

from .. import database
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
        hace = f"hace {segundos}s" if segundos < 60 else f"hace {segundos // 60}min"
    else:
        hace = "sin datos aún"

    todo_bien = online == total
    color = "#0ca30c" if todo_bien else "#fab219"
    punto = "🟢" if todo_bien else "🟡"

    texto = f"{punto} {online}/{total} en línea · última revisión {hace}"
    ancho = 40 + len(texto) * 7

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="32">
  <rect width="100%" height="100%" rx="6" fill="#0d0d0d" stroke="{color}" stroke-width="1.5"/>
  <text x="14" y="20" font-family="system-ui, -apple-system, Segoe UI, sans-serif" font-size="13" fill="#ffffff">{texto}</text>
</svg>"""

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache, max-age=60"},
    )
