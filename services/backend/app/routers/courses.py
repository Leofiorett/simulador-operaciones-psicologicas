import json
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..auth import get_current_user
from ..db import get_db
from ..models import ModuleProgress, User

router = APIRouter(prefix="/api/courses", tags=["courses"])

CURRICULUM_DIR = Path(config.SRC_DIR) / "curriculum"
QUIZ_DIR = CURRICULUM_DIR / "quizzes"
MODULO_RE = re.compile(r"^modulo-(\d+)-(.+)\.md$")


def _module_files():
    files = sorted(CURRICULUM_DIR.glob("modulo-*.md"))
    out = []
    for f in files:
        m = MODULO_RE.match(f.name)
        if not m:
            continue
        first_line = f.read_text(encoding="utf-8").splitlines()[0]
        titulo = first_line.lstrip("# ").strip()
        out.append({"slug": f.stem, "numero": int(m.group(1)),
                    "titulo": titulo, "archivo": f.name})
    return out


@router.get("")
async def list_modules():
    return {"modulos": _module_files()}


@router.get("/{slug}")
async def get_module(slug: str):
    if "/" in slug or "\\" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="Slug inválido")
    path = CURRICULUM_DIR / f"{slug}.md"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Módulo inexistente")
    quiz_path = QUIZ_DIR / f"{slug}.json"
    tiene_quiz = quiz_path.is_file()
    return {"slug": slug, "contenido": path.read_text(encoding="utf-8"),
            "tiene_cuestionario": tiene_quiz}


@router.get("/{slug}/quiz")
async def get_quiz(slug: str, user: User = Depends(get_current_user)):
    if "/" in slug or ".." in slug:
        raise HTTPException(status_code=400, detail="Slug inválido")
    quiz_path = QUIZ_DIR / f"{slug}.json"
    if not quiz_path.is_file():
        raise HTTPException(status_code=404, detail="Sin cuestionario")
    data = json.loads(quiz_path.read_text(encoding="utf-8"))
    preguntas_sin_respuesta = [
        {k: p[k] for k in ("pregunta", "opciones")}
        for p in data["preguntas"]
    ]
    return {"modulo": slug, "preguntas": preguntas_sin_respuesta}


class QuizSubmit(BaseModel):
    respuestas: list[int]


@router.post("/{slug}/quiz")
async def submit_quiz(slug: str, body: QuizSubmit,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    quiz_path = QUIZ_DIR / f"{slug}.json"
    if not quiz_path.is_file():
        raise HTTPException(status_code=404, detail="Sin cuestionario")
    data = json.loads(quiz_path.read_text(encoding="utf-8"))
    correctas = [p["correcta"] for p in data["preguntas"]]
    if len(body.respuestas) != len(correctas):
        raise HTTPException(status_code=400,
                            detail="Cantidad de respuestas incorrecta")
    score = sum(1 for r, c in zip(body.respuestas, correctas) if r == c)
    total = len(correctas)
    aprobado = score >= 0.7 * total

    existing = await db.execute(
        select(ModuleProgress).where(
            ModuleProgress.user_id == user.id,
            ModuleProgress.module_slug == slug))
    progress = existing.scalar_one_or_none()
    if progress is None:
        progress = ModuleProgress(user_id=user.id, module_slug=slug)
        db.add(progress)
    if score > progress.quiz_score or progress.attempts == 0:
        progress.quiz_score = score
        progress.quiz_total = total
    progress.completed = progress.completed or aprobado
    progress.attempts += 1
    await db.commit()

    detalle = [{"indice": i, "correcta": c, "elegida": r,
                "explicacion": data["preguntas"][i]["explicacion"]}
               for i, (r, c) in enumerate(zip(body.respuestas, correctas))]
    return {"score": score, "total": total, "aprobado": aprobado,
            "detalle": detalle}


@router.get("/progress/mine")
async def my_progress(user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(ModuleProgress).where(ModuleProgress.user_id == user.id))
    modulos_totales = len(_module_files())
    progreso = [
        {"module_slug": p.module_slug, "quiz_score": p.quiz_score,
         "quiz_total": p.quiz_total, "completed": p.completed,
         "attempts": p.attempts}
        for p in rows.scalars()
    ]
    completados = sum(1 for p in progreso if p["completed"])
    return {
        "progreso": progreso,
        "modulos_totales": modulos_totales,
        "completados": completados,
        "porcentaje_curso": round(100 * completados / max(1, modulos_totales)),
    }
