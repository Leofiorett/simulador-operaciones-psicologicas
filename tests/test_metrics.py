import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simulation.engine import Agent
from simulation.metrics import (mean, polarization_index, reach_pct,
                                segment_metrics, std)


def _poblacion_stub():
    agentes = []
    for i in range(100):
        seg = "a" if i < 60 else "b"
        agentes.append(Agent(i, seg,
                             0.5 if seg == "a" else -0.5, {}, 1.0))
        if i < 80:
            agentes[-1].expuesto = True
    return agentes


def test_mean_std():
    assert mean([1.0, 2.0, 3.0]) == 2.0
    assert std([5.0, 5.0]) == 0.0


def test_polarizacion_detecta_division():
    valores = [0.6] * 50 + [-0.6] * 50
    p = polarization_index(valores)
    assert p > 0.4
    assert polarization_index([0.0] * 50) < p


def test_reach_pct():
    assert reach_pct([True, True, False, False]) == 0.5
    assert reach_pct([]) == 0.0


def test_segment_metrics_atributos():
    agentes = _poblacion_stub()
    m = segment_metrics(agentes, segment="a")
    assert m["n"] == 60
    assert abs(m["actitud_media"] - 0.5) < 0.001

    flags = {a.id: a.expuesto for a in agentes}
    m_all = segment_metrics(agentes, exposed_flags=flags)
    assert abs(m_all["alcance"] - 0.8) < 0.01
