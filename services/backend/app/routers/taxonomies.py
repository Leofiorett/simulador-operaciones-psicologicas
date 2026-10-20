import json
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

from .. import config

sys.path.insert(0, config.SRC_DIR)

from simulation.biases import BIASES  # noqa: E402
from simulation.channels import CHANNELS  # noqa: E402

router = APIRouter(prefix="/api/taxonomies", tags=["taxonomies"])

TAX_DIR = Path(config.SRC_DIR) / "taxonomies"


def _load(name):
    path = TAX_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Taxonomía ausente: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/disarm-es")
async def disarm():
    data = _load("disarm_es.json")
    tecnicas = [
        {"id": t["id"],
         "nombre": t.get("nombre_es") or t.get("nombre_original"),
         "tactica": t.get("tactica_es"),
         "descripcion": t.get("resumen")}
        for t in data.get("tecnicas", [])
    ]
    return {"marco": data.get("marco"), "nota": data.get("nota"),
            "total_tecnicas": len(tecnicas), "tecnicas": tecnicas}


@router.get("/cwm")
async def cwm():
    data = _load("cwm_es.json")
    tecnicas = [
        {"id": f"CWM-T{i:02d}", **t, "categoria": "weaponización cognitiva"}
        for i, t in enumerate(data.get("tecnicas", []), start=1)
        if isinstance(t, dict) and "nombre" in t
    ]
    conceptos = [
        {"id": f"CWM-C{i:02d}", **c}
        for i, c in enumerate(data.get("conceptos_clave", []), start=1)
        if isinstance(c, dict) and "nombre" in c
    ]
    return {"marco": data.get("marco"), "nota": data.get("nota"),
            "total_tecnicas": len(tecnicas),
            "tecnicas": tecnicas, "conceptos": conceptos}


@router.get("/canales", tags=["catalogs"])
async def canales():
    return [{"code": k, **v} for k, v in CHANNELS.items()]


@router.get("/sesgos", tags=["catalogs"])
async def sesgos():
    return [{"id": k, **v, "factor": v.get("peso_base", 0.5)}
            for k, v in BIASES.items()]
