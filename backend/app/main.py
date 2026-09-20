import logging
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
def root():
    return {"ok": True, "service": "portfolio-status-api"}


@app.on_event("startup")
def on_startup():
    start_scheduler()
    # Corre un primer chequeo enseguida, en un hilo aparte, para que el
    # dashboard no quede vacío esperando el primer intervalo completo.
    threading.Thread(target=check_all_projects, daemon=True).start()
