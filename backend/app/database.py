"""
Conexión a Oracle Autonomous Database.

Render no deja archivos guardados entre despliegues, así que el wallet
(las credenciales de conexión que da Oracle) no se puede simplemente
"copiar" al servidor como se hizo con PRPagos en otros lados. En vez de
eso, el wallet completo (el .zip que descargas desde OCI) se guarda
codificado en base64 dentro de una sola variable de entorno
(ORACLE_WALLET_B64), y cada vez que arranca el backend, este archivo
lo decodifica y lo escribe en una carpeta temporal antes de conectarse.

En local (tu PC), si ya tienes la carpeta del wallet descomprimida en
disco, puedes simplemente apuntar TNS_ADMIN a esa carpeta en tu .env
local y dejar ORACLE_WALLET_B64 vacío — el código de abajo lo detecta
solo.
"""

import base64
import io
import os
import zipfile
from pathlib import Path

import oracledb

from .config import settings

WALLET_DIR = Path("/tmp/oracle_wallet")

_pool = None


def _setup_wallet() -> str | None:
    """Escribe el wallet en disco a partir de la variable de entorno,
    si hace falta. Devuelve la carpeta a usar como TNS_ADMIN, o None
    si no hay wallet configurado (ej. conexión sin wallet en desarrollo)."""

    if os.environ.get("TNS_ADMIN"):
        # Ya viene configurado desde afuera (típico en desarrollo local)
        return os.environ["TNS_ADMIN"]

    if not settings.ORACLE_WALLET_B64:
        return None

    WALLET_DIR.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(settings.ORACLE_WALLET_B64)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(WALLET_DIR)

    return str(WALLET_DIR)


def get_pool():
    global _pool
    if _pool is None:
        wallet_dir = _setup_wallet()
        _pool = oracledb.create_pool(
            user=settings.ORACLE_USER,
            password=settings.ORACLE_PASSWORD,
            dsn=settings.ORACLE_DSN,
            config_dir=wallet_dir,
            wallet_location=wallet_dir,
            wallet_password=settings.ORACLE_WALLET_PASSWORD or None,
            min=1,
            max=4,
            increment=1,
        )
    return _pool


def insert_check(proyecto: str, url: str, status_code: int | None, tiempo_ms: int | None, disponible: bool):
    pool = get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO CHECKS_LOG (PROYECTO, URL, STATUS_CODE, TIEMPO_MS, DISPONIBLE)
                VALUES (:proyecto, :url, :status_code, :tiempo_ms, :disponible)
                """,
                proyecto=proyecto,
                url=url,
                status_code=status_code,
                tiempo_ms=tiempo_ms,
                disponible=1 if disponible else 0,
            )
        conn.commit()


def fetch_latest_per_project():
    """Un registro por proyecto: el chequeo más reciente."""
    pool = get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT PROYECTO, STATUS_CODE, TIEMPO_MS, DISPONIBLE, CHECKED_AT
                FROM (
                    SELECT PROYECTO, STATUS_CODE, TIEMPO_MS, DISPONIBLE, CHECKED_AT,
                           ROW_NUMBER() OVER (PARTITION BY PROYECTO ORDER BY CHECKED_AT DESC) AS RN
                    FROM CHECKS_LOG
                )
                WHERE RN = 1
                """
            )
            cols = [c[0].lower() for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_uptime_percent(proyecto: str, dias: int = 7):
    pool = get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ROUND(100 * AVG(DISPONIBLE), 1) AS UPTIME_PCT,
                       ROUND(AVG(TIEMPO_MS)) AS AVG_MS
                FROM CHECKS_LOG
                WHERE PROYECTO = :proyecto
                  AND CHECKED_AT >= SYSTIMESTAMP - :dias
                """,
                proyecto=proyecto,
                dias=dias,
            )
            row = cur.fetchone()
            return {"uptime_pct": row[0] or 0, "avg_ms": row[1] or 0}


def fetch_history(proyecto: str, puntos: int = 14):
    """Últimos N chequeos de un proyecto, del más viejo al más nuevo
    (así el frontend los pinta de izquierda a derecha directo)."""
    pool = get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM (
                    SELECT DISPONIBLE, TIEMPO_MS, CHECKED_AT
                    FROM CHECKS_LOG
                    WHERE PROYECTO = :proyecto
                    ORDER BY CHECKED_AT DESC
                    FETCH FIRST :puntos ROWS ONLY
                )
                ORDER BY CHECKED_AT ASC
                """,
                proyecto=proyecto,
                puntos=puntos,
            )
            cols = [c[0].lower() for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
