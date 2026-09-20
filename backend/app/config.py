import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Oracle
    ORACLE_USER = os.environ.get("ORACLE_USER", "PORTFOLIO_STATUS")
    ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "")
    # Alias de conexión dentro del wallet, ej: "prpagos_high" o el que uses.
    ORACLE_DSN = os.environ.get("ORACLE_DSN", "")
    # El wallet.zip completo, codificado en base64, para poder guardarlo
    # como una sola variable de entorno en Render (no tiene filesystem
    # persistente donde dejar los archivos del wallet).
    ORACLE_WALLET_B64 = os.environ.get("ORACLE_WALLET_B64", "")
    ORACLE_WALLET_PASSWORD = os.environ.get("ORACLE_WALLET_PASSWORD", "")

    # Cada cuántos minutos se revisan los proyectos
    CHECK_INTERVAL_MINUTES = int(os.environ.get("CHECK_INTERVAL_MINUTES", "5"))

    # Dominio del frontend en Vercel, para permitirle llamar a esta API
    ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173")

    # Cuánto esperar como máximo la respuesta de cada proyecto antes de
    # darlo por caído en ese chequeo
    HTTP_TIMEOUT_SECONDS = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "10"))


settings = Settings()
