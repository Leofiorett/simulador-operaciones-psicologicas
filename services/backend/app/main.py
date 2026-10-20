from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, models  # noqa: F401
from .db import Base, SessionLocal, engine
from .auth import hash_password
from .models import User
from .routers import auth, courses, exercises_router, health, simulation, taxonomies

DEFAULT_USERS = [
    ("instructor", "sop-instructor-2026", "instructor",
     "Instructor Responsable"),
    ("alumno", "sop-alumno-2026", "alumno", "Alumno Unidad"),
]


async def ensure_seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from sqlalchemy import select
    async with SessionLocal() as db:
        for username, password, role, display in DEFAULT_USERS:
            existing = await db.execute(
                select(User).where(User.username == username))
            user = existing.scalar_one_or_none()
            if user is None:
                db.add(User(username=username,
                            password_hash=hash_password(password),
                            role=role, display_name=display))
            elif user.password_hash.startswith(("seed-", "$")) or \
                    "$" not in user.password_hash:
                user.password_hash = hash_password(password)
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_seed()
    yield


app = FastAPI(
    title="Simulador de Operaciones Psicológicas (SOP)",
    description="Plataforma de instrucción OPSIC — audiencias sintéticas en "
                "entorno aislado. Uso institucional autorizado.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(taxonomies.router)
app.include_router(simulation.router)
app.include_router(exercises_router.router)
