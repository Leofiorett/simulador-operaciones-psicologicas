# Simulador de Operaciones Psicológicas (SOP)

Plataforma de adiestramiento en **Operaciones Psicológicas (OPSIC/PSYOP)** para unidades de inteligencia, basada en el marco doctrinal del Gral. Harold K. Johnson — *"Operaciones psicológicas. Técnicas y procedimientos"* (Editorial Rioplatense, Buenos Aires, 1974) — reconstruido desde fuentes doctrinales públicas equivalentes.

## Advertencia

> ⚠️ Plataforma de **instrucción institucional** en entorno controlado. Todas las simulaciones corren contra **audiencias 100% sintéticas** dentro de una red Docker aislada. No existe conectividad con medios ni redes sociales reales. El uso está reservado a personal autorizado en el marco de la instrucción de fuerzas de defensa.

## Descripción

El sistema combina tres componentes:

1. **Currícula doctrinal** — 8 módulos que cubren el marco conceptual de la OPSIC clásica (acción sicológica vs. operación sicológica, niveles estratégico/operativo/táctico, propaganda blanca/gris/negra, análisis de audiencias, maniobra psicológica, medios, evaluación) extendidos con módulos de contrainfluencia y encuadre legal.
2. **Motor de simulación multiagente** — poblaciones sintéticas con actitudes, sesgos cognitivos (catálogo CWM) y grafo social; campañas definidas por segmento, idea-fuerza, canal y frecuencia; métricas de efecto (desplazamiento de actitud, alcance, polarización).
3. **Ciclo de ejercicios** — ejercicios guiados (`doctrina`, `planificacion`, `simulacion`, `defensa`) con ciclo de vida completo: metadata, evidencias, logs, timeout y reporte final.

Las taxonomías de detección usan los marcos **DISARM (español)** y la **Matriz de Armamentización Cognitiva (CWM)**.

## Requisitos

- Ubuntu 22.04+ / Debian
- Docker 24+ y Docker Compose v2
- Python 3.11+ (para tests del motor)
- Node.js 20+ (solo si se reconstruye el frontend fuera de Docker)

## Inicio rápido

```bash
make setup          # dependencias locales (venv + pytest)
sudo make deploy    # levanta db, redis, backend y frontend
make health-check   # verifica servicios
```

- Interfaz web: `http://localhost:8090`
- API: `http://localhost:8001/docs`

## Gestión de ejercicios

```bash
make exercise-start TYPE=simulacion NAME="Crisis humanitaria"
make exercise-status
make exercise-report ID=ex-XXXX
sudo make exercise-reset      # ¡borra datos! hacer backup antes
```

## Estructura

```
├── Makefile                  # interfaz de operaciones
├── docker-compose.yml        # db / redis / backend / frontend
├── services/
│   ├── backend/              # FastAPI (routers: courses, exercises, simulation, taxonomies)
│   ├── database/             # schema PostgreSQL
│   └── frontend/             # React + Vite + nginx
├── src/
│   ├── curriculum/           # 8 módulos Markdown + cuestionarios JSON
│   ├── simulation/           # motor multiagente
│   ├── exercises/            # lifecycle, evaluator, reports
│   └── taxonomies/           # DISARM-es + CWM curadas
├── data/
│   ├── exercises/ex-*/       # metadata.json, findings/, logs/, evidence/
│   ├── backups/  snapshots/
└── tests/                    # pytest (motor + ciclo de vida)
```

## Módulos curriculares

| # | Módulo |
|---|--------|
| 1 | Fundamentos e historia de la guerra psicológica |
| 2 | Marco conceptual OPSIC (Johnson): acción vs. operación sicológica, niveles, propaganda blanca/gris/negra |
| 3 | Análisis de audiencias objetivo |
| 4 | Maniobra psicológica: idea-fuerza, temas y símbolos |
| 5 | Medios y canales de difusión |
| 6 | Evaluación de efectividad |
| 7 | Contrainfluencia y defensa (DISARM-es + CWM) |
| 8 | Marco legal y ético |

## Documentación

- `docs/arquitectura.md` — arquitectura técnica
- `docs/manual-instructor.md` — manual del instructor

## Licencia

Uso institucional autorizado.
