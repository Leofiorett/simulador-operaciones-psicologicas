import json
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config  # noqa: E402

sys.path.insert(0, config.SRC_DIR)

from exercises import lifecycle  # noqa: E402
from exercises.reports import generate_report, save_report  # noqa: E402

from ..auth import get_current_user  # noqa: E402
from ..db import get_db  # noqa: E402
from ..models import Exercise, ExerciseEvent, User  # noqa: E402

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


def _sync_db(db: AsyncSession, meta: dict):
    async def _write():
        row = await db.get(Exercise, meta["id"])
        if row is None:
            row = Exercise(id=meta["id"])
            db.add(row)
        row.type = meta["type"]
        row.name = meta["name"]
        row.status = meta["status"]
        row.authorized_by = meta.get("authorized_by")
        row.owner_username = meta.get("owner")
        row.scenario_code = meta.get("scenario_code")
        row.results = meta.get("results")
        row.started_at = meta.get("started_at")
        row.ended_at = meta.get("ended_at")
        await db.commit()
    return _write()


class CreateIn(BaseModel):
    type: str
    name: str
    scenario_code: str | None = None


class StartIn(BaseModel):
    authorized_by: str | None = None


class CompleteIn(BaseModel):
    results: dict | None = None


@router.get("")
async def list_all(user: User = Depends(get_current_user)):
    lifecycle.check_timeouts(config.DATA_DIR)
    return {"ejercicios": lifecycle.list_exercises(config.DATA_DIR)}


@router.post("")
async def create(body: CreateIn, user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    try:
        meta = lifecycle.create_exercise(config.DATA_DIR, body.type, body.name,
                                         owner=user.username,
                                         scenario_code=body.scenario_code)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await _sync_db(db, meta)
    return meta


@router.get("/{exercise_id}")
async def detail(exercise_id: str,
                 user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    try:
        meta = lifecycle.load_metadata(config.DATA_DIR, exercise_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    events = await db.execute(
        select(ExerciseEvent).where(
            ExerciseEvent.exercise_id == exercise_id)
        .order_by(ExerciseEvent.ts.desc()).limit(100))
    eventos = [{"ts": str(e.ts), "event": e.event_type, "payload": e.payload}
               for e in events.scalars()]
    log_path = Path(config.DATA_DIR) / "exercises" / exercise_id / \
        "logs" / "events.log"
    if log_path.exists() and not eventos:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
                eventos.append({"ts": ev.get("ts"),
                                "event": ev.get("event"),
                                "payload": ev.get("payload", {})})
            except json.JSONDecodeError:
                continue
    evidencias = sorted(
        (Path(config.DATA_DIR) / "exercises" / exercise_id / "evidence")
        .glob("*")) if (Path(config.DATA_DIR) / "exercises" /
                        exercise_id / "evidence").is_dir() else []
    return {"metadata": meta,
            "eventos": eventos,
            "evidencias": [e.name for e in evidencias]}


@router.post("/{exercise_id}/start")
async def start(exercise_id: str, body: StartIn,
                user: User = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
    authorized_by = body.authorized_by or (
        user.display_name or user.username
        if user.role == "instructor" else None)
    try:
        meta = lifecycle.start_exercise(config.DATA_DIR, exercise_id,
                                        authorized_by=authorized_by)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    lifecycle.log_event(config.DATA_DIR, exercise_id, "db-sync",
                        {"by": user.username})
    await _sync_db(db, meta)
    return meta


@router.post("/{exercise_id}/stop")
async def stop(exercise_id: str, user: User = Depends(get_current_user),
               db: AsyncSession = Depends(get_db)):
    try:
        meta = lifecycle.stop_exercise(config.DATA_DIR, exercise_id,
                                       reason=f"detenido por {user.username}")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await _sync_db(db, meta)
    return meta


@router.post("/{exercise_id}/complete")
async def complete(exercise_id: str, body: CompleteIn,
                   user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    try:
        meta = lifecycle.complete_exercise(config.DATA_DIR, exercise_id,
                                           results=body.results)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await _sync_db(db, meta)
    return meta


@router.post("/{exercise_id}/report")
async def report(exercise_id: str, user: User = Depends(get_current_user)):
    try:
        meta = lifecycle.load_metadata(config.DATA_DIR, exercise_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    eventos = []
    log_path = Path(config.DATA_DIR) / "exercises" / exercise_id / \
        "logs" / "events.log"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                eventos.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    contenido = generate_report({**meta, "_dir":
                                 str(log_path.parent.parent)}, eventos=eventos)
    out = save_report(config.DATA_DIR, exercise_id, contenido)
    return {"reporte": contenido, "archivo": str(out)}
