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
