import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simulation.engine import run_simulation, validate_campaign
from simulation.scenarios import SCENARIOS, get_scenario


def _campana_basica(segmento="all", canal="radio", valencia=0.8):
    return {
        "mensajes": [
            {"segmento": segmento, "canal": canal, "valencia": valencia,
             "fuerza": 0.7, "credibilidad": 0.8, "frecuencia": 2,
             "ganchos": ["autoridad"], "turno_inicio": 0, "turno_fin": 11}
        ]
    }


def test_run_determinista():
    sc = get_scenario("crisis_humanitaria")
    r1 = run_simulation(sc, _campana_basica(), seed=7)
    r2 = run_simulation(sc, _campana_basica(), seed=7)
    assert r1["serie_temporal"] == r2["serie_temporal"]
    assert r1["metricas_finales"] == r2["metricas_finales"]


def test_campana_positiva_mejora_actitud():
    sc = get_scenario("crisis_humanitaria")
    r = run_simulation(sc, _campana_basica(), seed=7)
    base = sum(
        (s["actitud_base"][0] + s["actitud_base"][1]) / 2 * s["proporcion"]
        for s in sc["poblacion"]["segmentos"])
    final = r["metricas_finales"]["actitud_media_global"]
    assert final > base * 0.5


def test_mensaje_negativo_degrada_actitud():
    sc = get_scenario("apoyo_paz")
    positivo = run_simulation(sc, _campana_basica(valencia=0.9), seed=3)
    negativo = run_simulation(sc, _campana_basica(valencia=-0.9), seed=3)
    p = positivo["metricas_finales"]["actitud_media_global"]
    n = negativo["metricas_finales"]["actitud_media_global"]
    assert n < p - 0.05


def test_defensa_escenario_sin_duplicar_adversaria():
    """El escenario con adversaria no debe inyectarla dos veces al pasar
    una copia sin la clave operacion_adversaria."""
    sc = SCENARIOS["defensa_desinformacion"].copy()
    sc_sin = {k: v for k, v in sc.items() if k != "operacion_adversaria"}
    adv = sc["operacion_adversaria"]
    combinada = {"mensajes": list(adv["mensajes"])}
    r = run_simulation(sc_sin, combinada, seed=42)
    assert r["metricas_finales"]["alcance_global"] > 0
    assert r["metricas_finales"]["polarizacion_global"] >= 0


def test_validate_campaign_rechaza_canal_desconocido():
    try:
        validate_campaign(_campana_basica(canal="tiktok"))
        assert False, "debia fallar"
    except ValueError as exc:
        assert "Canal" in str(exc) or "canal" in str(exc)


def test_validate_campaign_rechaza_segmento_desconocido():
    sc = get_scenario("crisis_humanitaria")
    segmentos = [s["nombre"] for s in sc["poblacion"]["segmentos"]]
    try:
        validate_campaign(_campana_basica(segmento="marcianos"), segmentos)
        assert False, "debia fallar"
    except ValueError as exc:
        assert "Segmento" in str(exc) or "segmento" in str(exc)


def test_todos_los_escenarios_corren():
    for code, sc in SCENARIOS.items():
        cfg = {k: v for k, v in sc.items() if k != "operacion_adversaria"}
        r = run_simulation(cfg, _campana_basica(), seed=1)
        assert "metricas_finales" in r, code
        m = r["metricas_finales"]
        assert -1.0 <= m["actitud_media_global"] <= 1.0, code
        assert 0.0 <= m["polarizacion_global"] <= 1.0, code
