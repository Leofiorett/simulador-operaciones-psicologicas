# Arquitectura — Simulador de Operaciones Psicológicas (SOP)

Plataforma de instrucción OPSIC para unidades de inteligencia, basada en el
marco doctrinal del Gral. H. K. Johnson (1974) reconstruido desde fuentes
públicas equivalentes (FM 33-1, JP 3-53, doctrina OTAN PsyOps/MISO).

**Alcance:** instrucción institucional contra audiencias 100% sintéticas en
red aislada. Sin salida a internet, sin conexión con medios reales.

---

## Vista general

```
┌──────────────┐   /api/*    ┌─────────────────┐            ┌────────────┐
│  Frontend    │────────────▶│  Backend FastAPI │──asyncpg──▶│ PostgreSQL │
│  React+Vite  │             │  (uvicorn :8000) │            │   (sop)    │
│  nginx :80   │             └───────┬─────────┘            └────────────┘
└──────────────┘                     │
                                     ▼
                              ┌────────────┐      ┌─────────────────────┐
                              │ Redis 7    │      │ Motor de simulación │
                              │ (cache)    │      │ src/simulation/*    │
                              └────────────┘      │ (montado read-only) │
                                                  └─────────────────────┘
```

Todo dentro de la red Docker `sop-net` (172.90.0.0/16), sin puertos salientes.

## Servicios (docker-compose.yml)

| Servicio  | Imagen base          | Puerto host | Puerto contenedor | Volumen |
|-----------|----------------------|-------------|-------------------|---------|
| `db`      | postgres:16-alpine   | 5433        | 5432              | `sop_postgres_data` |
| `redis`   | redis:7-alpine       | 6380        | 6379              | `sop_redis_data` |
| `backend` | python:3.12-slim     | 8001        | 8000              | `./data:/app/data`, `./src:/app/src:ro` |
| `frontend`| node build + nginx   | 8090        | 80                | — |

Variables relevantes (`config/settings.example.env` → copiar a `.env`):
`SOP_DB_PASSWORD`, `SOP_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`,
`SOP_DATA_DIR=/app/data`, `SOP_SRC_DIR=/app/src`.

## Backend (services/backend/app/)

- **main.py** — FastAPI + lifespan que crea tablas y siembra usuarios por
  defecto (`instructor` / `alumno`, contraseñas hasheadas con PBKDF2 al vuelo).
- **auth.py** — PBKDF2-HMAC-SHA256 (120k iteraciones, formato `salt$hash`),
  tokens HMAC-SHA256 firmados (`base64url(payload).sig`), dependencias
  `get_current_user` y `require_instructor`.
- **routers/**
  - `health.py` — `/api/health`
  - `auth.py` — `POST /api/auth/login`, `GET /api/auth/me`
  - `courses.py` — currícula: listar módulos, contenido Markdown,
    cuestionarios GET/POST (aprobar ≥70%), progreso propio.
  - `taxonomies.py` — DISARM-es normalizado, CWM, catálogos de canales y
    sesgos del motor.
  - `simulation.py` — `GET /scenarios`, `POST /run` (campaña ofensiva o de
    apoyo), `POST /defensa` (línea base adversaria vs. campaña combinada),
    persiste campañas/runs en PostgreSQL y evidencia en el ejercicio activo.
  - `exercises_router.py` — CRUD de ejercicios sobre `src/exercises/lifecycle.py`,
    espejo de metadata en la tabla `exercises`.

## Motor de simulación (src/simulation/) — Python puro

Determinista por semilla. Sin dependencias externas.

- **engine.py** — `Agent` (actitud, susceptibilidad por sesgo, exposición a
  medios, fatiga por canal), población segmentada, grafo social small-world
  simplificado (anillo + recableo), bucle por turnos:
  - efecto = fuerza × credibilidad_efectiva × susceptibilidad_promedio ×
    afinidad_canal-ganchos × exposición × (1 − distancia_actitud×0.7) × LR
  - `LEARNING_RATE=0.22`, propagación interpersonal atenuada (0.40).
  - Fatiga por canal reduce credibilidad efectiva con la sobreexposición.
- **channels.py** — 5 canales doctrinales: impresos, radio, altavoces,
  red digital sintética, acción cívica/interpersonal.
- **biases.py** — 12 ganchos cognitivos (autoridad, miedo-FUD, prueba social,
  negatividad, escasez, confirmación, polarización grupal, verdad ilusoria,
  disponibilidad, indefension aprendida, anclaje, efecto halo).
- **metrics.py** — actitud media, desviación, índice de polarización
  (σ + bimodalidad de Sarle), alcance acumulado.
- **scenarios.py** — 3 escenarios sintéticos precargados:
  - `crisis_humanitaria` (4 segmentos; objetivos: actitud ≥0.05, pol ≤0.55, alcance ≥0.65)
  - `apoyo_paz` (4 segmentos; persuasión/desmoralización controlada)
  - `defensa_desinformacion` (3 segmentos + operación adversaria inyectada;
    el alumno diseña contramedidas).

## Ejercicios (src/exercises/) — patrón cyber range

Ciclo: `created → running → completed | stopped | timeout` (timeout 24 h).

```
data/exercises/ex-YYYYmmdd-HHMMSS-NNNN/
├── metadata.json    # estado, autorización, resultados, escenario
├── findings/        # hallazgos .md del alumno
├── logs/events.log  # bitácora JSONL (created/started/stopped/db-sync…)
└── evidence/        # runs de simulación, reportes
```

Reglas duras: iniciar requiere `authorized_by` (instructor responsable);
completar solo desde `running`; detener desde `created|running`.

Evaluadores (`evaluator.py`): `doctrina` (50% precisión cuestionarios +
50% módulos completos), `planificacion` (rúbrica de 6 criterios, ≥70),
`simulacion` (objetivos del escenario, score 60–100 según margen), `defensa`
(5 criterios vs. línea base solo-adversaria, ≥60).

## Currícula y taxonomías (src/)

- `curriculum/modulo-01..08.md` — fundamentos, análisis psicológico,
  planificación, propaganda blanca/gris/negra, canales, producción de
  material, contra-propaganda y guerra psicológica, marco legal/DIH.
- `curriculum/quizzes/modulo-01..08.json` — 8 preguntas c/u con explicación.
- `taxonomies/disarm_es.json` — 71 técnicas DISARM traducidas al español
  (generadas desde el SQLite oficial de DISARMframeworks-es).
- `taxonomies/cwm_es.json` — Matriz de Weaponización Cognitiva (40 técnicas
  + conceptos), curada localmente.

## Base de datos

Tablas: `users`, `module_progress`, `exercises`, `exercise_events`,
`campaigns`, `simulation_runs` (ver `services/database/init.sql`).

## Flujo defensivo (importante)

`run_simulation()` agrega automáticamente `scenario_cfg["operacion_adversaria"]`.
Para evaluar defensa se pasa una **copia del escenario sin esa clave** y los
mensajes del adversario se fusionan manualmente en la campaña combinada:
1. línea base = escenario sin adversaria + mensajes adversarios
2. defensa = escenario sin adversaria + mensajes alumno + mensajes adversarios
3. `evaluate_defensa(defensa, linea_base)` compara ambos.

## Seguridad / límites

- Red interna única, sin `extra_hosts`, sin DNS público necesario.
- El motor corre en memoria; nada toca redes externas.
- Autenticación obligatoria salvo health-check.
- Todo endpoint de escritura queda trazado en bitácora/evidencia.
