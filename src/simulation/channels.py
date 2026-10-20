"""Canales de difusion sinteticos del simulador.

Cada canal modela alcance por turno, propagacion interpersonal, fatiga
(decadencia de credibilidad con la sobreexposicion) y afinidad con sesgos.
"""

CHANNELS = {
    "impresos": {
        "nombre": "Impresos (volantes, cartillas)",
        "alcance_por_turno": 0.35,
        "propagacion_interpersonal": 0.05,
        "fatiga_por_turno": 0.04,
        "credibilidad_base": 0.70,
        "afinidad_sesgos": {"verdad_ilusoria": 1.2, "anclaje": 1.1},
    },
    "radio": {
        "nombre": "Radio (programas y boletines)",
        "alcance_por_turno": 0.70,
        "propagacion_interpersonal": 0.02,
        "fatiga_por_turno": 0.03,
        "credibilidad_base": 0.75,
        "afinidad_sesgos": {"autoridad": 1.3, "prueba_social": 1.1, "verdad_ilusoria": 1.2},
    },
    "altavoces": {
        "nombre": "Altavoces (acción directa de zona)",
        "alcance_por_turno": 0.25,
        "propagacion_interpersonal": 0.01,
        "fatiga_por_turno": 0.10,
        "credibilidad_base": 0.55,
        "afinidad_sesgos": {"miedo_fud": 1.4, "escasez": 1.2},
    },
    "digital_sintetico": {
        "nombre": "Red digital sintética (medios sociales simulados)",
        "alcance_por_turno": 0.80,
        "propagacion_interpersonal": 0.25,
        "fatiga_por_turno": 0.08,
        "credibilidad_base": 0.45,
        "afinidad_sesgos": {
            "prueba_social": 1.4,
            "negatividad": 1.3,
            "sesgo_confirmacion": 1.2,
            "polarizacion_grupal": 1.3,
        },
    },
    "interpersonal": {
        "nombre": "Acción cívica / contacto directo",
        "alcance_por_turno": 0.12,
        "propagacion_interpersonal": 0.30,
        "fatiga_por_turno": 0.01,
        "credibilidad_base": 0.85,
        "afinidad_sesgos": {"prueba_social": 1.5, "efecto_halo": 1.2},
    },
}


def get_channel(code):
    return CHANNELS.get(code)


def validate_channel(code):
    if code not in CHANNELS:
        raise ValueError(f"Canal desconocido: {code}. Validos: {sorted(CHANNELS)}")
