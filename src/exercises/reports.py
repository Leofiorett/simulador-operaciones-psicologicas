"""Generacion de reportes de ejercicio (Markdown)."""

import json
from datetime import datetime
from pathlib import Path


def _fmt_ts(iso):
    if not iso:
        return "-"
    return iso.replace("T", " ").split(".")[0]


def generate_report(metadata, eventos=None):
    eid = metadata["id"]
    lineas = [
        f"# Reporte de ejercicio {eid}",
        "",
        f"- **Nombre:** {metadata['name']}",
        f"- **Tipo:** {metadata['type']}",
        f"- **Estado:** {metadata['status']}",
        f"- **Responsable de autorizacion:** {metadata.get('authorized_by') or 'NO AUTORIZADO'}",
        f"- **Creado:** {_fmt_ts(metadata.get('created_at'))}",
        f"- **Iniciado:** {_fmt_ts(metadata.get('started_at'))}",
        f"- **Finalizado:** {_fmt_ts(metadata.get('ended_at'))}",
        f"- **Escenario:** {metadata.get('scenario_code') or '-'}",
        f"- **Generado:** {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    results = metadata.get("results")
    if results:
        lineas += ["## Resultados", ""]
        lineas.append(f"- **Puntaje:** {results.get('score', '-')} / 100")
        lineas.append(f"- **Aprobado:** {'SÍ' if results.get('aprobado') else 'NO'}")
        for k, v in results.items():
            if k in ("score", "aprobado"):
                continue
            lineas.append(f"- **{k}:** `{json.dumps(v, ensure_ascii=False)[:400]}`")
        lineas.append("")
    else:
        lineas += ["## Resultados", "", "_Sin resultados registrados._", ""]

    dir_base = metadata.get("_dir")
    hallazgos = []
    if dir_base:
        findings_dir = Path(dir_base) / "findings"
        hallazgos = sorted(findings_dir.glob("*.md")) if findings_dir.is_dir() else []
    if hallazgos:
        lineas += ["## Hallazgos registrados", ""]
        for h in hallazgos:
            primera = h.read_text(encoding="utf-8").strip().splitlines()
            titulo = next((l.lstrip("# ") for l in primera if l.strip()), h.stem)
            lineas.append(f"- `{h.name}` — {titulo}")
        lineas.append("")

    if eventos:
        lineas += ["## Bitácora de eventos", "", "| Momento | Evento | Detalle |",
                   "|---|---|---|"]
        for ev in eventos:
            detalle = json.dumps(ev.get("payload", {}), ensure_ascii=False)
            lineas.append(
                f"| {_fmt_ts(ev.get('ts'))} | {ev.get('event')} | {detalle[:120]} |")
        lineas.append("")

    lineas += [
        "## Advertencia de clasificación",
        "",
        "Material de instrucción institucional. Simulación contra audiencias "
        "sintéticas en entorno aislado; no aplica a poblaciones reales.",
        "",
    ]
    return "\n".join(lineas)


def save_report(data_dir, exercise_id, contenido):
    d = Path(data_dir) / "exercises" / exercise_id
    out = d / "evidence" / "report.md"
    out.write_text(contenido, encoding="utf-8")
    return out
