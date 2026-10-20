"""Escenarios sinteticos precargados del simulador.

Cada escenario define una poblacion ficticia, sus segmentos, la topologia
social, los objetivos de instruccion y opcionalmente una operacion adversaria
inyectada (para ejercicios de defensa).
"""

from .biases import BIASES


def _susceptibilidad_uniforme():
    return {b: 1.0 for b in BIASES}


SCENARIOS = {
    "crisis_humanitaria": {
        "code": "crisis_humanitaria",
        "nombre": "Crisis humanitaria - zona afectada por desastre",
        "descripcion": (
            "Poblacion sintetica afectada por un desastre natural con corte de "
            "servicios. Circulan rumores sobre desabastecimiento que erosionan la "
            "cooperacion con la respuesta estatal. El alumno debe planificar una "
            "campana de accion sicológica (aspecto defensivo) para sostener la "
            "cooperacion, desmentir rumores y apoyar la labor de las agencias."
        ),
        "tipo_sugerido": "simulacion",
        "poblacion": {
            "tamano": 1200,
            "vecinos": 6,
            "recableo": 0.15,
            "segmentos": [
                {"nombre": "comunidad_local", "proporcion": 0.50,
                 "actitud_base": [-0.10, 0.25],
                 "exposicion_medios": [0.8, 1.2]},
                {"nombre": "desplazados", "proporcion": 0.30,
                 "actitud_base": [-0.40, 0.00],
                 "susceptibilidad": {"miedo_fud": 1.5, "disponibilidad": 1.4,
                                     "indefension_aprendida": 1.4},
                 "exposicion_medios": [0.6, 1.1]},
                {"nombre": "lideres_comunitarios", "proporcion": 0.08,
                 "actitud_base": [0.30, 0.60],
                 "susceptibilidad": {"autoridad": 1.3},
                 "exposicion_medios": [1.0, 1.5]},
                {"nombre": "grupo_agitador", "proporcion": 0.12,
                 "actitud_base": [-0.80, -0.45],
                 "susceptibilidad": {"negatividad": 1.5, "polarizacion_grupal": 1.5},
                 "exposicion_medios": [1.0, 1.6]},
            ],
        },
        "objetivos": {
            "actitud_media_min": 0.05,
            "polarizacion_max": 0.55,
            "alcance_min": 0.65,
        },
        "turnos_default": 24,
    },

    "apoyo_paz": {
        "code": "apoyo_paz",
        "nombre": "Operación de apoyo a la paz - proceso de pacificación",
        "descripcion": (
            "Zona sintetica bajo operacion multinacional de paz. Se busca que "
            "grupos armados irregulares acepten el cese y la entrega voluntaria "
            "de armas, y que la poblacion colabore informando ubicaciones de "
            "arsenales. Ejercicio clasico de operacion sicológica ofensiva "
            "(persuasion y desmoralizacion controlada del adversario armado)."
        ),
        "tipo_sugerido": "planificacion",
        "poblacion": {
            "tamano": 1200,
            "vecinos": 5,
            "recableo": 0.20,
            "segmentos": [
                {"nombre": "poblacion_civil", "proporcion": 0.55,
                 "actitud_base": [0.00, 0.30],
                 "exposicion_medios": [0.8, 1.2]},
                {"nombre": "combatientes_mediobajo", "proporcion": 0.20,
                 "actitud_base": [-0.60, -0.20],
                 "susceptibilidad": {"indefension_aprendida": 1.5,
                                     "escasez": 1.3, "prueba_social": 1.2},
                 "exposicion_medios": [0.5, 1.0]},
                {"nombre": "mandos_irregulares", "proporcion": 0.07,
                 "actitud_base": [-0.95, -0.70],
                 "susceptibilidad": {"sesgo_confirmacion": 1.6},
                 "exposicion_medios": [0.7, 1.0]},
                {"nombre": "comunidad_receptora", "proporcion": 0.18,
                 "actitud_base": [-0.20, 0.20],
                 "susceptibilidad": {"prueba_social": 1.3},
                 "exposicion_medios": [0.9, 1.3]},
            ],
        },
        "objetivos": {
            "actitud_media_min": 0.02,
            "polarizacion_max": 0.60,
            "alcance_min": 0.60,
        },
        "turnos_default": 24,
    },

    "defensa_desinformacion": {
        "code": "defensa_desinformacion",
        "nombre": "Defensa contra operación extranjera de desinformación",
        "descripcion": (
            "Una potencia adversaria conduce una operacion de influencia contra "
            "la poblacion sintetica (operacion adversaria ya inyectada en el "
            "escenario) para erosinar la confianza institucional y polarizar. "
            "El alumno actua en el rol DEFENSIVO: detectar las tecnicas en curso "
            "usando las taxonomias DISARM/CWM y disenar contramedidas "
            "(inoculacion, contramensaje veraz, coordinacion interinstitucional)."
        ),
        "tipo_sugerido": "defensa",
        "operacion_adversaria": {
            "mensajes": [
                {"segmento": "urbanos_conectados", "canal": "digital_sintetico",
                 "valencia": -0.85, "fuerza": 0.75, "credibilidad": 0.55,
                 "frecuencia": 4, "ganchos": ["negatividad", "polarizacion_grupal",
                                              "verdad_ilusoria"],
                 "turno_inicio": 0, "turno_fin": 23},
                {"segmento": "rurales", "canal": "radio",
                 "valencia": -0.60, "fuerza": 0.55, "credibilidad": 0.70,
                 "frecuencia": 2, "ganchos": ["miedo_fud", "autoridad"],
                 "turno_inicio": 2, "turno_fin": 23},
            ],
        },
        "poblacion": {
            "tamano": 1200,
            "vecinos": 6,
            "recableo": 0.18,
            "segmentos": [
                {"nombre": "urbanos_conectados", "proporcion": 0.55,
                 "actitud_base": [0.10, 0.35],
                 "susceptibilidad": {"sesgo_confirmacion": 1.3,
                                     "prueba_social": 1.3},
                 "exposicion_medios": [1.1, 1.8]},
                {"nombre": "rurales", "proporcion": 0.30,
                 "actitud_base": [0.00, 0.25],
                 "susceptibilidad": {"autoridad": 1.3},
                 "exposicion_medios": [0.6, 1.0]},
                {"nombre": "funcionarios_y_fuerzas", "proporcion": 0.15,
                 "actitud_base": [0.40, 0.75],
                 "susceptibilidad": {},
                 "exposicion_medios": [0.9, 1.3]},
            ],
        },
        "objetivos_defensivos": {
            "descripcion": ("Mantener actitud media positiva y contener la "
                            "polarizacion pese a la operacion adversaria."),
            "actitud_media_min": 0.10,
            "polarizacion_max": 0.45,
        },
        "turnos_default": 24,
    },
}


def list_scenarios():
    out = []
    for code, sc in SCENARIOS.items():
        out.append({
            "code": code,
            "nombre": sc["nombre"],
            "descripcion": sc["descripcion"],
            "tipo_sugerido": sc.get("tipo_sugerido"),
            "segmentos": [
                {"nombre": s["nombre"], "proporcion": s["proporcion"],
                 "actitud_base": s["actitud_base"]}
                for s in sc["poblacion"]["segmentos"]
            ],
            "tiene_operacion_adversaria": bool(sc.get("operacion_adversaria")),
            "objetivos": sc.get("objetivos") or sc.get("objetivos_defensivos"),
            "turnos_default": sc.get("turnos_default", 24),
        })
    return out


def get_scenario(code):
    return SCENARIOS.get(code)
