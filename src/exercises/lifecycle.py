"""Ciclo de vida de ejercicios del SOP (patron cyber range).

Cada ejercicio vive en data/exercises/ex-*/ con:
  metadata.json | findings/ | logs/ | evidence/
Estados: created -> running -> completed|stopped|timeout
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXERCISE_TYPES = ("doctrina", "planificacion", "simulacion", "defensa")
STATUSES = ("created", "running", "completed", "stopped", "timeout")


def _now():
    return datetime.now(timezone.utc)


def _ex_dir(data_dir, exercise_id):
    d = Path(data_dir) / "exercises" / exercise_id
    if not d.is_dir():
        raise FileNotFoundError(f"Ejercicio inexistente: {exercise_id}")
    return d


def _meta_path(d):
    return d / "metadata.json"


def load_metadata(data_dir, exercise_id):
    p = _meta_path(_ex_dir(data_dir, exercise_id))
    return json.loads(p.read_text(encoding="utf-8"))


def save_metadata(data_dir, exercise_id, meta):
    p = _meta_path(_ex_dir(data_dir, exercise_id))
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def log_event(data_dir, exercise_id, event_type, payload=None):
    d = _ex_dir(data_dir, exercise_id)
    ts = _now().isoformat()
    line = json.dumps({"ts": ts, "event": event_type,
                       "payload": payload or {}}, ensure_ascii=False)
    with open(d / "logs" / "events.log", "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def create_exercise(data_dir, tipo, nombre, owner=None, scenario_code=None,
                    authorized_by=None, timeout_hours=24):
    if tipo not in EXERCISE_TYPES:
        raise ValueError(f"Tipo invalido: {tipo}. Validos: {EXERCISE_TYPES}")
    ts = _now().strftime("%Y%m%d-%H%M%S")
    eid = f"ex-{ts}-{random.randint(1000, 9999)}"
    d = Path(data_dir) / "exercises" / eid
    for sub in ("findings", "logs", "evidence"):
        (d / sub).mkdir(parents=True, exist_ok=True)

    meta = {
        "id": eid,
        "type": tipo,
        "name": nombre,
        "status": "created",
        "owner": owner,
        "scenario_code": scenario_code,
        "authorized_by": authorized_by,
        "timeout_hours": timeout_hours,
        "config": {},
        "results": None,
        "created_at": _now().isoformat(),
        "started_at": None,
        "ended_at": None,
    }
    save_metadata(data_dir, eid, meta)
    log_event(data_dir, eid, "created", {"type": tipo, "name": nombre})
    return meta


def start_exercise(data_dir, exercise_id, authorized_by=None):
    meta = load_metadata(data_dir, exercise_id)
    if meta["status"] != "created":
        raise ValueError(f"No se puede iniciar ejercicio en estado {meta['status']}")
    autoridad = authorized_by or meta.get("authorized_by")
    if not autoridad:
        raise PermissionError(
            "Ejercicio sin autorizacion: requiere authorized_by (instructor responsable)")
    meta["status"] = "running"
    meta["started_at"] = _now().isoformat()
    meta["authorized_by"] = autoridad
    save_metadata(data_dir, exercise_id, meta)
    log_event(data_dir, exercise_id, "started", {"authorized_by": autoridad})
    return meta


def stop_exercise(data_dir, exercise_id, reason="manual"):
    meta = load_metadata(data_dir, exercise_id)
    if meta["status"] not in ("created", "running"):
        raise ValueError(f"No se puede detener ejercicio en estado {meta['status']}")
    meta["status"] = "stopped"
    meta["ended_at"] = _now().isoformat()
    save_metadata(data_dir, exercise_id, meta)
    log_event(data_dir, exercise_id, "stopped", {"reason": reason})
    return meta


def complete_exercise(data_dir, exercise_id, results=None):
    meta = load_metadata(data_dir, exercise_id)
    if meta["status"] != "running":
        raise ValueError(f"No se puede completar ejercicio en estado {meta['status']}")
    meta["status"] = "completed"
    meta["ended_at"] = _now().isoformat()
    if results is not None:
        meta["results"] = results
    save_metadata(data_dir, exercise_id, meta)
    log_event(data_dir, exercise_id, "completed",
              {"score": (results or {}).get("score")})
    return meta


def check_timeouts(data_dir):
    """Marca timeout los ejercicios running vencidos. Devuelve ids afectados."""
    timed_out = []
    base = Path(data_dir) / "exercises"
    if not base.is_dir():
        return timed_out
    for d in sorted(base.glob("ex-*")):
        try:
            meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("status") != "running":
            continue
        inicio = datetime.fromisoformat(meta["started_at"])
        limite = timedelta(hours=meta.get("timeout_hours", 24))
        if _now() - inicio > limite:
            meta["status"] = "timeout"
            meta["ended_at"] = _now().isoformat()
            save_metadata(data_dir, meta["id"], meta)
            log_event(data_dir, meta["id"], "timeout", {})
            timed_out.append(meta["id"])
    return timed_out


def list_exercises(data_dir):
    base = Path(data_dir) / "exercises"
    out = []
    if not base.is_dir():
        return out
    for d in sorted(base.glob("ex-*"), reverse=True):
        try:
            out.append(json.loads(
                (d / "metadata.json").read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out
