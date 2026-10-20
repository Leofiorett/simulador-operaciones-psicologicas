import json
import sys
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config  # noqa: E402

sys.path.insert(0, config.SRC_DIR)

from simulation import run_simulation, validate_campaign  # noqa: E402
from simulation.scenarios import get_scenario, list_scenarios  # noqa: E402
from exercises.evaluator import evaluate_defensa, evaluate_simulacion  # noqa: E402

from ..auth import get_current_user  # noqa: E402
from ..db import get_db  # noqa: E402
from ..models import Campaign, SimulationRun, User  # noqa: E402

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class RunIn(BaseModel):
    escenario: str
    campana: dict
    semilla: int | None = None
    turnos: int | None = None
    ejercicio_id: str | None = None


class DefensaIn(BaseModel):
    escenario: str
    campana_defensiva: dict
    semilla: int | None = None
    ejercicio_id: str | None = None


def _save_evidence(ejercicio_id, nombre_archivo, datos):
    if not ejercicio_id:
        return None
    d = Path(config.DATA_DIR) / "exercises" / ejercicio_id / "evidence"
    if not d.is_dir():
        raise HTTPException(status_code=404,
                            detail="Ejercicio inexistente para evidencia")
    out = d / nombre_archivo
    out.write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    return str(out)


@router.get("/scenarios")
async def scenarios():
    return {"escenarios": list_scenarios()}


@router.post("/run")
async def run(body: RunIn, user: User = Depends(get_current_user),
              db: AsyncSession = Depends(get_db)):
    sc = get_scenario(body.escenario)
    if not sc:
        raise HTTPException(status_code=404, detail="Escenario desconocido")
    try:
        validate_campaign(body.campana)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    seed = body.semilla if body.semilla is not None else 42
    try:
        resultado = run_simulation(sc, body.campana, seed=seed,
                                   ticks=body.turnos)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    evaluacion = evaluate_simulacion(resultado)
    respuesta = {"simulacion": resultado, "evaluacion": evaluacion}

    evidencia = {
        "tipo": "simulacion",
        "operador": user.username,
        "semilla": seed,
        "campana": body.campana,
        "metricas_finales": resultado["metricas_finales"],
        "evaluacion": evaluacion,
    }
    _save_evidence(body.ejercicio_id, f"run-{uuid.uuid4().hex[:8]}.json",
                   evidencia)

    camp = Campaign(exercise_id=body.ejercicio_id,
                    name=f"camp-{user.username}-{seed}",
                    scenario_code=body.escenario, config=body.campana,
                    created_by=user.username)
    db.add(camp)
    await db.flush()
    db.add(SimulationRun(id=str(uuid.uuid4()), campaign_id=camp.id,
                         scenario_code=body.escenario, seed=seed,
                         metrics=resultado["metricas_finales"],
                         series={"serie_temporal": resultado["serie_temporal"]}))
    await db.commit()
    return respuesta


@router.post("/defensa")
async def run_defensa(body: DefensaIn, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    sc = get_scenario(body.escenario)
    if not sc:
        raise HTTPException(status_code=404, detail="Escenario desconocido")
    if "operacion_adversaria" not in sc:
        raise HTTPException(
            status_code=400,
            detail="El escenario no incluye operación adversaria inyectada")

    try:
        validate_campaign(body.campana_defensiva)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    seed = body.semilla if body.semilla is not None else 42

    esc_sin_adversaria = {k: v for k, v in sc.items()
                          if k != "operacion_adversaria"}
    lineabase = run_simulation(esc_sin_adversaria,
                               sc["operacion_adversaria"], seed=seed)

    combinada = {
        "mensajes": list(body.campana_defensiva.get("mensajes", []))
        + list(sc["operacion_adversaria"]["mensajes"])
    }
    defensa = run_simulation(esc_sin_adversaria, combinada, seed=seed)

    evaluacion = evaluate_defensa(defensa, lineabase)
    respuesta = {
        "linea_base": lineabase["metricas_finales"],
        "defensa": defensa["metricas_finales"],
        "serie_defensa": defensa["serie_temporal"],
        "evaluacion": evaluacion,
    }

    evidencia = {
        "tipo": "defensa",
        "operador": user.username,
        "semilla": seed,
        "campana_defensiva": body.campana_defensiva,
        "evaluacion": evaluacion,
    }
    _save_evidence(body.ejercicio_id, f"defensa-{uuid.uuid4().hex[:8]}.json",
                   evidencia)

    await db.commit()
    return respuesta
