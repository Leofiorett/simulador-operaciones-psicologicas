# AGENTS.md - Simulador de Operaciones Psicológicas (SOP)

## Overview

Plataforma de adiestramiento en Operaciones Psicológicas (OPSIC/PSYOP) para unidades de inteligencia, basada en el marco doctrinal del Gral. Harold K. Johnson ("Operaciones psicológicas. Técnicas y procedimientos", Ed. Rioplatense, 1974), reconstruido desde fuentes doctrinales públicas equivalentes (FM 33-1, JP 3-53, doctrina OTAN PsyOps/MISO).

**Uso exclusivo: instrucción institucional en entorno controlado con audiencias 100% sintéticas.**

---

## Critical Commands

### Setup (One-Time)
```bash
make setup          # Crea venv Python, instala dependencias del motor de simulación
sudo make deploy    # Levanta todos los servicios Docker
make validate       # Valida configuración del entorno
make health-check   # Verifica salud de servicios
```

### Gestión de Ejercicios
```bash
# Tipos: doctrina, planificacion, simulacion, defensa
make exercise-start TYPE=doctrina NAME="Modulo inicial"
make exercise-status
make exercise-stop ID=ex-XXXX
make exercise-reset            # BORRA datos permanentemente - hacer backup antes
make exercise-report ID=ex-XXXX
```

### Operación diaria
```bash
make status                # Estado de contenedores
make logs SERVICE=backend  # Logs de un servicio
make test                  # Tests pytest del motor y ciclo de vida
make backup                # Backup completo a data/backups/
sudo make cleanup          # Limpieza de datos antiguos
```

---

## Architecture

### Entry Point
- **Makefile** — interfaz principal (simulador-operaciones-psicologicas/Makefile)

### Key Directories
- `services/backend/` — API FastAPI + SQLAlchemy async (app/main.py, routers/)
- `services/database/` — init.sql (schema PostgreSQL)
- `services/frontend/` — SPA React + Vite servida por nginx
- `src/simulation/` — motor multiagente (población sintética, canales, métricas)
- `src/exercises/` — ciclo de vida de ejercicios y reportes
- `src/curriculum/` — 8 módulos doctrinales Markdown + cuestionarios JSON
- `src/taxonomies/` — DISARM-es y Matriz CWM curadas (técnicas de influencia)
- `data/exercises/ex-*` — cada ejercicio: metadata.json, findings/, logs/, evidence/

### Service Dependencies
PostgreSQL → Redis → backend → frontend (orden de arranque)

### Network
Red interna aislada `sop-net` (172.90.0.0/16). El motor de simulación NO tiene salida a internet ni conexión con medios reales.

---

## Critical Constraints

- **Audiencias sintéticas solamente**: prohibido conectar el simulador a redes sociales o medios reales.
- Los ejercicios requieren autorización del instructor responsable antes de iniciarlos.
- `exercise-reset` borra datos permanentemente — usar `make backup` primero.
- Backups críticos en `data/backups/`.
- Todo el contenido doctrinal es material de instrucción; verificar encuadre legal (DIH) en el Módulo 8.

---

## Warning Flags

⚠️ Plataforma de INSTRUCCIÓN — no constituye herramienta de operación sobre poblaciones reales
⚠️ Uso exclusivo institucional autorizado
⚠️ Reset de ejercicios borra evidencia permanentemente
