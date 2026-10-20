"""Evaluacion automatica de ejercicios por tipo."""

import re


def evaluate_doctrina(progress_rows):
    """progress_rows: [{module_slug, quiz_total, quiz_score, completed}]"""
    if not progress_rows:
        return {"score": 0, "detalle": "sin avance registrado", "aprobado": False}
    total_modulos = len(progress_rows)
    completados = sum(1 for r in progress_rows if r.get("completed"))
    pct_score = sum(
        (r.get("quiz_score", 0) / r.get("quiz_total", 1))
        for r in progress_rows if r.get("quiz_total")
    ) / total_modulos
    score = round(100 * 0.5 * pct_score + 100 * 0.5 * (completados / total_modulos), 1)
    return {
        "score": score,
        "aprobado": completados == total_modulos and pct_score >= 0.7,
        "modulos_completados": completados,
        "total_modulos": total_modulos,
        "precision_promedio_cuestionarios": round(pct_score, 3),
    }


RUBRICA_PLANIFICACION = [
    ("idea_fuerza_definida",
     "Existe idea-fuerza unica y coherente con el objetivo psicologico"),
    ("segmentacion_precisa",
     "La campana apunta a segmentos especificos, no a toda la poblacion"),
    ("canales_combinados",
     "Uso de al menos dos canales complementarios"),
    ("frecuencia_sostenible",
     "Frecuencia media <= 3 para evitar fatiga y perdida de credibilidad"),
    ("credibilidad_suficiente",
     "Credibilidad declarada >= 0.6 en todos los mensajes"),
    ("ganchos_declarados",
     "Todo mensaje declara sus ganchos cognitivos (transparencia doctrinal)"),
]


def evaluate_planificacion(campaign_cfg):
    mensajes = campaign_cfg.get("mensajes", [])
    checks = {}
    checks["idea_fuerza_definida"] = bool(campaign_cfg.get("idea_fuerza"))
    segmentos = {m.get("segmento") for m in mensajes}
    checks["segmentacion_precisa"] = bool(mensajes) and "all" not in segmentos
    canales = {m.get("canal") for m in mensajes}
    checks["canales_combinados"] = len(canales) >= 2
    freqs = [int(m.get("frecuencia", 1)) for m in mensajes] or [0]
    checks["frecuencia_sostenible"] = sum(freqs) / len(freqs) <= 3.0
    creds = [float(m.get("credibilidad", 0)) for m in mensajes] or [0]
    checks["credibilidad_suficiente"] = min(creds) >= 0.6
    checks["ganchos_declarados"] = all(m.get("ganchos") for m in mensajes)

    cumplidos = sum(1 for v in checks.values() if v)
    score = round(100 * cumplidos / len(RUBRICA_PLANIFICACION), 1)
    detalle = {
        clave: {"cumplido": valor, "criterio": desc}
        for (clave, desc), valor in zip(RUBRICA_PLANIFICACION,
                                        [checks[k] for k, _ in RUBRICA_PLANIFICACION])
    }
    return {"score": score, "aprobado": score >= 70, "rubrica": detalle}


def evaluate_simulacion(sim_result):
    objetivos = sim_result.get("objetivos", {})
    cumplidos = objetivos.get("cumplidos", {})
    aprobado = objetivos.get("aprobado")
    final = sim_result["metricas_finales"]
    margen = 0.0
    meta = objetivos.get("meta", {})
    if "actitud_media_min" in meta:
        margen += max(0.0, final["actitud_media_global"] - meta["actitud_media_min"])
    if "polarizacion_max" in meta:
        margen += max(0.0, meta["polarizacion_max"] - final["polarizacion_global"])
    if "alcance_min" in meta:
        margen += max(0.0, final["alcance_global"] - meta["alcance_min"])
    score = round(min(100.0, 60 + 400 * margen) if aprobado else
                  max(0.0, 60 * sum(1 for v in cumplidos.values() if v)
                      / max(1, len(cumplidos))), 1)
    return {"score": score, "aprobado": bool(aprobado),
            "objetivos_cumplidos": cumplidos, "metricas": final}


def evaluate_defensa(result_defensa, result_adversario_base):
    """Compara la defensa del alumno contra la linea base solo-adversaria."""
    fd = result_defensa["metricas_finales"]
    fb = result_adversario_base["metricas_finales"]
    mejora_actitud = fd["actitud_media_global"] - fb["actitud_media_global"]
    mejora_polarizacion = fb["polarizacion_global"] - fd["polarizacion_global"]

    criterios = {
        "actitud_sostenida": fd["actitud_media_global"] >= 0.10,
        "mejora_vs_linea_base": mejora_actitud >= 0.05,
        "polarizacion_contenida": fd["polarizacion_global"] <= 0.45,
        "mejora_polarizacion_vs_base": mejora_polarizacion >= 0.02,
        "cobertura_alta": fd["alcance_global"] >= 0.55,
    }
    score = round(100 * sum(1 for v in criterios.values() if v) / len(criterios), 1)
    return {
        "score": score,
        "aprobado": score >= 60,
        "criterios": criterios,
        "mejora_actitud": round(mejora_actitud, 4),
        "mejora_polarizacion": round(mejora_polarizacion, 4),
        "metricas_defensa": fd,
        "metricas_linea_base": fb,
    }


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "hallazgo"
