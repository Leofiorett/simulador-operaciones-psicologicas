"""Metricas de efecto para el motor de simulacion."""

import math


def mean(values):
    return sum(values) / len(values) if values else 0.0


def std(values):
    if not values:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def polarization_index(values):
    """Indice de polarizacion: desviacion estandar + bimodalidad (coef. de Sarle).

    0.0 = consenso total en el centro; valores altos = poblacion dividida.
    """
    if len(values) < 2:
        return 0.0
    s = std(values)
    m = mean(values)
    denom = len(values) * (s ** 3)
    skew = (
        sum((v - m) ** 3 for v in values) / denom
        if denom > 0 and s > 0
        else 0.0
    )
    bimodality = skew ** 2 + 1.0
    return round(min(1.0, 0.6 * s + 0.4 * bimodality / 3.0), 4)


def reach_pct(exposed_flags):
    if not exposed_flags:
        return 0.0
    return round(sum(1 for e in exposed_flags if e) / len(exposed_flags), 4)


def segment_metrics(agents, segment=None, baseline=None, exposed_flags=None):
    pool = [a for a in agents if segment is None or a.segment == segment]
    attitudes = [a.attitude for a in pool]
    out = {
        "n": len(pool),
        "actitud_media": round(mean(attitudes), 4),
        "desviacion": round(std(attitudes), 4),
        "polarizacion": polarization_index(attitudes),
    }
    if baseline is not None:
        out["desplazamiento"] = round(out["actitud_media"] - baseline, 4)
    if exposed_flags is not None:
        flags = [
            exposed_flags[a.id] for a in pool
        ]
        out["alcance"] = reach_pct(flags)
    return out
