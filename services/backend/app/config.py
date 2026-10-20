import os


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # asyncpg no acepta sslmode (es un parámetro de libpq): se quita.
    if "sslmode=" in url:
        url = url.split("?", 1)[0]
    return url


_raw_db_url = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://sop:sop_pass_2026@db:5432/sop")
# SSL requerido para Postgres administrado (Render/Neon) fuera de la red local.
DB_SSL = "sslmode=require" in _raw_db_url or os.environ.get(
    "SOP_DB_SSL", "").lower() in ("1", "true", "yes")
DATABASE_URL = _normalize_db_url(_raw_db_url)
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
SECRET_KEY = os.environ.get("SOP_SECRET_KEY", "change-me-in-production")
DATA_DIR = os.environ.get("SOP_DATA_DIR", "/app/data")
SRC_DIR = os.environ.get("SOP_SRC_DIR", "/app/src")

TOKEN_TTL_HOURS = 12
PBKDF2_ITERATIONS = 120_000
