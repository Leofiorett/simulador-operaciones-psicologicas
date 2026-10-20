"""Catalogo de sesgos cognitivos explotables en simulacion (derivado de la Matriz CWM).

Cada sesgo define la susceptibilidad base de una audiencia sintetica y se usa como
"gancho" declarado en los mensajes de campana de entrenamiento.
"""

BIASES = {
    "sesgo_confirmacion": {
        "nombre": "Sesgo de confirmación",
        "descripcion": "Tendencia a aceptar información que confirma creencias preexistentes.",
        "peso_base": 0.55,
    },
    "anclaje": {
        "nombre": "Anclaje",
        "descripcion": "La primera información recibida condiciona juicios posteriores.",
        "peso_base": 0.50,
    },
    "negatividad": {
        "nombre": "Sesgo de negatividad",
        "descripcion": "Los hechos negativos pesan más que los positivos en la percepción.",
        "peso_base": 0.60,
    },
    "prueba_social": {
        "nombre": "Prueba social",
        "descripcion": "Se adopta conducta percibida como mayoritaria o creciente.",
        "peso_base": 0.65,
    },
    "autoridad": {
        "nombre": "Autoridad",
        "descripcion": "Mensajes emitidos por fuentes percibidas como legítimas ganan aceptación.",
        "peso_base": 0.60,
    },
    "escasez": {
        "nombre": "Efecto escasez",
        "descripcion": "Lo percibido como escaro u urgentemente limitado aumenta su valor.",
        "peso_base": 0.50,
    },
    "verdad_ilusoria": {
        "nombre": "Efecto de verdad ilusoria",
        "descripcion": "La repetición incrementa la percepción de veracidad.",
        "peso_base": 0.55,
    },
    "efecto_halo": {
        "nombre": "Efecto halo",
        "descripcion": "Una característica positiva positiva arrastra valoraciones globales.",
        "peso_base": 0.45,
    },
    "disponibilidad": {
        "nombre": "Heurística de disponibilidad",
        "descripcion": "Se sobreestima lo que es fácil de recordar o imaginarse.",
        "peso_base": 0.55,
    },
    "polarizacion_grupal": {
        "nombre": "Polarización grupal",
        "descripcion": "La discusión intragrupal radicaliza posiciones iniciales.",
        "peso_base": 0.50,
    },
    "indefension_aprendida": {
        "nombre": "Indefensión aprendida",
        "descripcion": "Exposición repetida a fracasos reduce la iniciativa de actuación.",
        "peso_base": 0.40,
    },
    "miedo_fud": {
        "nombre": "FUD (miedo, incertidumbre, duda)",
        "descripcion": "Estados emocionales de amenaza elevan receptividad a mensajes simples.",
        "peso_base": 0.70,
    },
}


def get_bias(bias_id):
    return BIASES.get(bias_id)


def validate_hooks(hooks):
    invalid = [h for h in hooks if h not in BIASES]
    if invalid:
        raise ValueError(f"Sesgos desconocidos: {invalid}. Validos: {sorted(BIASES)}")
