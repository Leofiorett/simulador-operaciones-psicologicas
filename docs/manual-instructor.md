# Manual del Instructor — SOP

Plataforma de instrucción en Operaciones Psicológicas (OPSIC) para la unidad.
Audiencias sintéticas exclusivamente; material basado en el manual del
Gral. H. K. Johnson (1974) reconstruido desde doctrina pública equivalente.

---

## 1. Acceso y roles

| URL | Servicio |
|---|---|
| http://localhost:8090 | Plataforma web |
| http://localhost:8001/docs | API interactiva (OpenAPI) |

Credenciales sembradas por defecto:

| Usuario | Contraseña | Rol |
|---|---|---|
| `instructor` | `sop-instructor-2026` | instructor (autoriza ejercicios) |
| `alumno` | `sop-alumno-2026` | alumno |

**Cambiar estas contraseñas antes del primer uso real.** El backend las
hashea con PBKDF2 al arrancar; para rotarlas, actualizar `DEFAULT_USERS` en
`services/backend/app/main.py` y redesplegar.

El rol instructor es el único que puede **autorizar e iniciar** ejercicios.

## 2. Recorrido curricular sugerido (8 módulos)

1. Fundamentos y marco conceptual
2. Análisis del entorno psicológico
3. Planificación de la operación sicológica
4. Propaganda blanca, gris y negra
5. Canales de difusión
6. Producción de material sicológico
7. Contra-propaganda y guerra psicológica
8. Marco legal y DIH

Cada módulo: lectura Markdown + cuestionario de comprensión (8 preguntas,
aprobado ≥70%, reintentos ilimitados, se conserva el mejor puntaje).
El progreso individual se ve en el Panel y en `/api/courses/progress/mine`.

**Evaluación de curso:** promedio 50% precisión de cuestionarios +
50% módulos aprobados (evaluador `doctrina`).

## 3. Tipos de ejercicio

| Tipo | Objetivo instruccional | Evaluación automática |
|---|---|---|
| `doctrina` | Comprensión teórica (8 módulos) | score combinado cuestionarios+completitud |
| `planificacion` | Diseñar campaña: idea-fuerza, segmentos, canales | rúbrica 6 criterios (≥70 aprueba) |
| `simulacion` | Ejecutar campaña contra escenario y cumplir objetivos | objetivos del escenario (score 60–100) |
| `defensa` | Detectar operación adversaria y contrarrestarla | 5 criterios vs. línea base (≥60 aprueba) |

## 4. Ciclo de vida

```
crear → [created] --iniciar (requiere autorización)--> [running]
[running] → completar → [completed]      # con resultados/score
[running] → detener   → [stopped]        # o timeout a las 24 h
```

- Solo `running` acepta evidencia de simulaciones (`evidence/`) y hallazgos.
- La bitácora `logs/events.log` registra todo (JSONL inmutable por diseño).
- Reporte Markdown generado a `evidence/report.md` (botón *Generar reporte*
  o `make exercise-report ID=...`).

### Por CLI

```bash
sudo make exercise-start TYPE=defensa NAME="Defensa desinfo - comisión A" \
      SCENARIO=defensa_desinformacion AUTHORIZED_BY="Tte. Coronel X"
make exercise-status
make exercise-report ID=ex-20260824-...
sudo make exercise-stop ID=ex-...
```

### Por web (rol instructor)

Ejercicios → Nuevo ejercicio → tipo/nombre/escenario → Crear → Iniciar.
Al iniciar como instructor, el sistema usa tu nombre visible como autoridad.

## 5. Escenarios disponibles

| Código | Situación sintética | Uso típico |
|---|---|---|
| `crisis_humanitaria` | Desastre natural, rumores de desabastecimiento; 4 segmentos (comunidad, desplazados, líderes, agitadores) | simulación de apoyo defensivo |
| `apoyo_paz` | Zona de pacificación multinacional; combatientes irregulares que deben entregar armas | simulación ofensiva/persuasiva |
| `defensa_desinformacion` | Potencia extranjera polariza vía red digital + radio rural (operación adversaria ya inyectada) | ejercicio de defensa |

Objetivos medibles por escenario (actitud mínima, polarización máxima,
alcance mínimo) — visibles al seleccionar escenario en el Simulador.

## 6. Conducir una práctica en clase (guion sugerido)

1. **Briefing (10 min):** escenario, segmentos, objetivos, reglas de
   compromiso (todo sintético, sin datos reales).
2. **Fase planificación:** los alumnos arman la campaña en papel o directo
   en el Simulador: idea-fuerza única, segmento objetivo, canal, valencia/
   fuerza/credibilidad/frecuencia, ganchos declarados, ventana de turnos.
3. **Ejecución:** botón *Ejecutar* (semilla fija p. ej. 42 para que toda la
   comisión reproduzca idéntico resultado).
4. **Debrief:** comparar métricas finales vs. objetivos; discutir fatiga de
   canal (frecuencia alta baja credibilidad efectiva), afinidad canal-gancho,
   distancia entre actitud base y valencia del mensaje.
5. **Variante defensa (escenario `defensa_desinformacion`):** identificar
   técnicas adversarias usando la pestaña Taxonomías (DISARM-es / CWM) y
   diseñar inoculación + contramensaje veraz; ejecutar *Ejecutar defensa*
   y revisar mejora vs. línea base.

## 7. Interpretando resultados

- **actitud media global:** −1..1 (positiva = favorable al mensaje propio).
- **polarización:** 0..1 (σ + bimodalidad); >0.55 indica población dividida.
- **alcance:** proporción de población expuesta alguna vez.
- **por segmento:** Δ (desplazamiento) por grupo; útil para evaluar
  segmentación (p. ej., mover `desplazados` sin activar `grupo_agitador`).
- Serie temporal: evolución turno a turno — buscar mesetas (fatiga) o rebotes.

Rúbrica planificación (los 6 checks del evaluador):
idea-fuerza definida · segmentación específica · ≥2 canales · frecuencia
media ≤3 · credibilidad ≥0.6 en todos los mensajes · ganchos declarados.

## 8. Operación y mantenimiento

```bash
make status                 # contenedores
make logs SERVICE=backend   # logs
make test                   # suite pytest (17 tests)
sudo make backup            # backup completo a data/backups/
sudo make restore TS=YYYYmmdd-HHMMSS
sudo make cleanup           # purga datos antiguos
```

⚠️ `make exercise-reset` borra TODOS los ejercicios permanentemente:
hacer backup antes si hay evidencia a preservar.

## 9. Reglas de seguridad

- Plataforma de instrucción: prohibido conectarla a redes sociales o medios
  reales; corre en red Docker aislada sin salida.
- Toda simulación queda trazada con usuario, semilla y campaña en PostgreSQL
  y en `evidence/`.
- Verificar encuadre legal/DIH (Módulo 8) antes de cada ciclo formativo.
