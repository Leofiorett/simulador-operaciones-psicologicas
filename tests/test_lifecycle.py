import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from exercises.lifecycle import (complete_exercise, create_exercise,
                                 load_metadata, start_exercise,
                                 stop_exercise)
from exercises.reports import generate_report


@pytest.fixture()
def ejercicio(tmp_path):
    return create_exercise(str(tmp_path), "simulacion",
                           "Prueba unitaria", owner="tester",
                           scenario_code="crisis_humanitaria")


def test_crear_ejercicio(ejercicio, tmp_path):
    assert ejercicio["status"] == "created"
    meta = load_metadata(str(tmp_path), ejercicio["id"])
    assert meta["name"] == "Prueba unitaria"


def test_start_requiere_autorizacion(tmp_path):
    ex = create_exercise(str(tmp_path), "doctrina", "Sin autorización")
    with pytest.raises(PermissionError):
        start_exercise(str(tmp_path), ex["id"], authorized_by=None)


def test_start_con_autorizacion(tmp_path):
    ex = create_exercise(str(tmp_path), "doctrina", "Con autorización")
    meta = start_exercise(str(tmp_path), ex["id"],
                          authorized_by="Instructor Responsable")
    assert meta["status"] == "running"
    assert meta["authorized_by"] == "Instructor Responsable"


def test_stop_y_complete(tmp_path, ejercicio):
    start_exercise(str(tmp_path), ejercicio["id"], authorized_by="Jefe")
    meta = stop_exercise(str(tmp_path), ejercicio["id"], reason="fin de prueba")
    assert meta["status"] == "stopped"
    with pytest.raises(ValueError):
        complete_exercise(str(tmp_path), ejercicio["id"], results={})


def test_tipo_invalido_rechazado(tmp_path):
    with pytest.raises(ValueError):
        create_exercise(str(tmp_path), "tipo-fantasma", "X")


def test_reporte_generable(tmp_path, ejercicio):
    start_exercise(str(tmp_path), ejercicio["id"], authorized_by="Jefe")
    meta = stop_exercise(str(tmp_path), ejercicio["id"])
    texto = generate_report(meta, eventos=[])
    assert ejercicio["id"] in texto
    assert "REPORTE" in texto.upper()
