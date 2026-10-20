import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://sop:sop_pass_2026@db:5432/sop")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
SECRET_KEY = os.environ.get("SOP_SECRET_KEY", "change-me-in-production")
DATA_DIR = os.environ.get("SOP_DATA_DIR", "/app/data")
SRC_DIR = os.environ.get("SOP_SRC_DIR", "/app/src")

TOKEN_TTL_HOURS = 12
PBKDF2_ITERATIONS = 120_000
