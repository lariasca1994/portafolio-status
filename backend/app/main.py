import logging
import threading

import oracledb
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import status
from .scheduler import check_all_projects, start_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Portfolio Status API",
    description="Revisa periódicamente si cada proyecto del portafolio sigue funcionando.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(status.router)


@app.exception_handler(oracledb.OperationalError)
@app.exception_handler(oracledb.InterfaceError)
def base_no_disponible(_request: Request, error: Exception):
    """Oracle apagado o inalcanzable: 503 con marca de mantenimiento (el panel
    muestra su pantalla de mantenimiento) en vez de un 500 genérico."""
    logging.getLogger(__name__).warning("Oracle no disponible: %s", type(error).__name__)
    return JSONResponse(status_code=503, headers={"Retry-After": "300"},
                        content={"detail": "servicio en mantenimiento", "mantenimiento": True})


@app.get("/")
def root():
    return {"ok": True, "service": "portfolio-status-api"}


@app.on_event("startup")
def on_startup():
    start_scheduler()
    # Corre un primer chequeo enseguida, en un hilo aparte, para que el
    # dashboard no quede vacío esperando el primer intervalo completo.
    threading.Thread(target=check_all_projects, daemon=True).start()
