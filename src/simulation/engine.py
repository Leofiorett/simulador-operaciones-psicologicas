"""Motor de simulacion multiagente del SOP.

Modela poblaciones sinteticas con actitudes, susceptibilidad a sesgos
cognitivos, grafo social y exposicion a campanas por canal. Todo corre
en memoria, de forma determinista (semilla reproducible) y sin acceso
a redes externas.
"""

import random

from .biases import BIASES, validate_hooks
from .channels import CHANNELS, validate_channel
from .metrics import mean, std, polarization_index

LEARNING_RATE = 0.22
SPREAD_ATTENUATION = 0.40


class Agent:
    __slots__ = ("id", "segment", "attitude", "susceptibility",
                 "exposicion_medios", "fatiga_canal", "expuesto")

    def __init__(self, agent_id, segment, attitude, susceptibility,
                 exposicion_medios):
        self.id = agent_id
        self.segment = segment
        self.attitude = attitude
        self.susceptibility = susceptibility
        self.exposicion_medios = exposicion_medios
        self.fatiga_canal = {}
        self.expuesto = False


def _rand_in(rng, rango):
    if isinstance(rango, (list, tuple)) and len(rango) == 2:
        return rng.uniform(rango[0], rango[1])
    return float(rango)


def build_population(poblacion_cfg, rng):
    agents = []
    agent_id = 0
    for seg in poblacion_cfg["segmentos"]:
        n = int(round(poblacion_cfg["tamano"] * seg["proporcion"]))
        base_susc = {b: v["peso_base"] for b, v in BIASES.items()}
        perfil = seg.get("susceptibilidad", {})
        for _ in range(n):
            susc = dict(base_susc)
            for b, mult in perfil.items():
                if b in susc:
                    susc[b] = min(1.0, susc[b] * mult)
            attitude = _rand_in(rng, seg["actitud_base"])
            expo = _rand_in(rng, seg.get("exposicion_medios", [0.8, 1.2]))
            agents.append(Agent(agent_id, seg["nombre"], attitude, susc, expo))
            agent_id += 1
    return agents


def build_network(agents, k, rewire_prob, rng):
    """Grafo small-world simplificado: anillo + recableo aleatorio."""
    n = len(agents)
    neighbors = [[] for _ in range(n)]
    half = max(1, k // 2)
    for i in range(n):
        for d in range(1, half + 1):
            a, b = i, (i + d) % n
            neighbors[a].append(b)
            neighbors[b].append(a)
    for i in range(n):
        if rng.random() < rewire_prob and neighbors[i]:
            old = neighbors[i][rng.randrange(len(neighbors[i]))]
            new = rng.randrange(n)
            if new != i and new not in neighbors[i]:
                neighbors[i].remove(old)
                neighbors[new].append(i)
    return neighbors


def validate_campaign(campaign_cfg, segmentos_validos=None):
    mensajes = campaign_cfg.get("mensajes")
    if not mensajes:
        raise ValueError("La campaña no define mensajes.")
    validos = set(segmentos_validos or ()) | {"all"}
    for m in mensajes:
        validate_channel(m["canal"])
        segmento = m.get("segmento", "all")
        if segmentos_validos is not None and segmento not in validos:
            raise ValueError(
                f"Segmento desconocido: {segmento}. Validos: {sorted(validos)}")
        hooks = m.get("ganchos", [])
        validate_hooks(hooks)
        if not -1.0 <= float(m.get("valencia", 0)) <= 1.0:
            raise ValueError("valencia fuera de rango [-1,1]")
        if not 0.0 <= float(m.get("fuerza", 0.5)) <= 1.0:
            raise ValueError("fuerza fuera de rango [0,1]")
        if not 0.0 <= float(m.get("credibilidad", 0.5)) <= 1.0:
            raise ValueError("credibilidad fuera de rango [0,1]")
        if not 1 <= int(m.get("frecuencia", 1)) <= 5:
            raise ValueError("frecuencia fuera de rango [1,5]")


def _affinity_media(channel, ganchos):
    afinidades = channel.get("afinidad_sesgos", {})
    if not ganchos:
        return 1.0
    return sum(afinidades.get(g, 1.0) for g in ganchos) / len(ganchos)


def run_simulation(scenario_cfg, campaign_cfg, seed=42, ticks=None):
    """Ejecuta una simulacion y devuelve metricas por turno y finales."""
    pob_cfg = scenario_cfg["poblacion"]
    segmentos_validos = [s["nombre"] for s in pob_cfg["segmentos"]]
    validate_campaign(campaign_cfg, segmentos_validos)
    rng = random.Random(seed)

    agents = build_population(pob_cfg, rng)
    neighbors = build_network(agents, pob_cfg.get("vecinos", 6),
                              pob_cfg.get("recableo", 0.15), rng)

    agents_by_segment = {}
    for a in agents:
        agents_by_segment.setdefault(a.segment, []).append(a)
    agents_all = {a.id: a for a in agents}

    mensajes = list(campaign_cfg["mensajes"])
    adversaria = scenario_cfg.get("operacion_adversaria")
    if adversaria:
        validate_campaign(adversaria, segmentos_validos)
        mensajes += adversaria["mensajes"]

    total_ticks = ticks or campaign_cfg.get("turnos",
                                            scenario_cfg.get("turnos_default", 24))

    baselines = {
        seg: mean([a.attitude for a in lst])
        for seg, lst in agents_by_segment.items()
    }
    series = []
    exposed_ids = set()

    for tick in range(total_ticks):
        for action in mensajes:
            if not (action.get("turno_inicio", 0) <= tick
                    <= action.get("turno_fin", total_ticks - 1)):
                continue
            target = action.get("segmento", "all")
            pool_map = (
                {"all": agents} if target == "all"
                else {target: agents_by_segment.get(target, [])}
            )
            for _, pool in pool_map.items():
                _run_single_action(pool, neighbors, agents_all,
                                   action, tick, rng, exposed_ids)

        attitudes = [a.attitude for a in agents]
        series.append({
            "turno": tick,
            "actitud_media": round(mean(attitudes), 4),
            "polarizacion": polarization_index(attitudes),
            "alcance_acumulado": round(len(exposed_ids) / len(agents), 4),
        })

    resultado = {
        "escenario": scenario_cfg["code"],
        "semilla": seed,
        "turnos": total_ticks,
        "poblacion_total": len(agents),
        "serie_temporal": series,
        "metricas_finales": {
            "actitud_media_global": series[-1]["actitud_media"],
            "polarizacion_global": series[-1]["polarizacion"],
            "alcance_global": series[-1]["alcance_acumulado"],
            "por_segmento": {},
        },
    }

    for seg, lst in agents_by_segment.items():
        attitudes = [a.attitude for a in lst]
        flags = [a.expuesto for a in lst]
        resultado["metricas_finales"]["por_segmento"][seg] = {
            "n": len(lst),
            "actitud_base": round(baselines[seg], 4),
            "actitud_final": round(mean(attitudes), 4),
            "desplazamiento": round(mean(attitudes) - baselines[seg], 4),
            "polarizacion": polarization_index(attitudes),
            "alcance": round(sum(flags) / len(flags), 4),
        }

    objetivos = scenario_cfg.get("objetivos", {})
    final_metrics = resultado["metricas_finales"]
    evaluacion = {}
    if "actitud_media_min" in objetivos:
        evaluacion["actitud_media_min"] = (
            final_metrics["actitud_media_global"] >= objetivos["actitud_media_min"])
    if "polarizacion_max" in objetivos:
        evaluacion["polarizacion_max"] = (
            final_metrics["polarizacion_global"] <= objetivos["polarizacion_max"])
    if "alcance_min" in objetivos:
        evaluacion["alcance_min"] = (
            final_metrics["alcance_global"] >= objetivos["alcance_min"])
    resultado["objetivos"] = {"meta": objetivos, "cumplidos": evaluacion,
                              "aprobado": all(evaluacion.values()) if evaluacion else None}

    return resultado


def _run_single_action(pool, neighbors, agents_all, action, tick, rng, exposed_ids):
    channel = CHANNELS[action["canal"]]
    ganchos = action.get("ganchos", [])
    valencia = float(action.get("valencia", 0.0))
    fuerza = float(action.get("fuerza", 0.5))
    credibilidad = float(action.get("credibilidad", 0.5))
    frecuencia = int(action.get("frecuencia", 1))

    if not pool:
        return []
    affinity = _affinity_media(channel, ganchos)
    intensidad = min(1.0, channel["alcance_por_turno"] * frecuencia * 0.6)

    nuevos_expuestos = []
    for agent in pool:
        if rng.random() > intensidad:
            continue
        fatiga = agent.fatiga_canal.get(action["canal"], 0.0)
        cred_efectiva = credibilidad * max(0.15, 1.0 - fatiga)
        hook_susc = (
            sum(agent.susceptibility.get(h, 0.4) for h in ganchos) / len(ganchos)
            if ganchos else 0.45
        )
        distancia = abs(agent.attitude - valencia) / 2.0
        efecto = (fuerza * cred_efectiva * hook_susc * affinity
                  * agent.exposicion_medios * (1.0 - distancia * 0.7)
                  * LEARNING_RATE)
        agent.attitude = max(-1.0, min(1.0, agent.attitude + valencia * efecto))
        fatiga_nueva = fatiga + channel["fatiga_por_turno"] * (1 + frecuencia * 0.3)
        agent.fatiga_canal[action["canal"]] = min(1.0, fatiga_nueva)
        if agent.id not in exposed_ids:
            exposed_ids.add(agent.id)
            agent.expuesto = True
            nuevos_expuestos.append(agent.id)

    prob_spread = channel["propagacion_interpersonal"] * max(cred_efectiva, 0.2)
    propagados = set()
    for aid in nuevos_expuestos:
        for nb in neighbors[aid]:
            if nb in propagados:
                continue
            vecino = agents_all[nb]
            if rng.random() < prob_spread * vecino.exposicion_medios:
                efecto_vecino = (fuerza * cred_efectiva * SPREAD_ATTENUATION
                                 * LEARNING_RATE * 0.5)
                vecino.attitude = max(-1.0, min(1.0,
                                      vecino.attitude + valencia * efecto_vecino))
                propagados.add(nb)
                if nb not in exposed_ids:
                    exposed_ids.add(nb)
                    vecino.expuesto = True
    return nuevos_expuestos
