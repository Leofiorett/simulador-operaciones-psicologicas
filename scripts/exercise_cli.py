#!/usr/bin/env python3
"""CLI de gestion de ejercicios del SOP (usado por el Makefile)."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT / "src"))

from exercises import lifecycle  # noqa: E402
from exercises.reports import generate_report, save_report  # noqa: E402


def cmd_start(args):
    meta = lifecycle.create_exercise(
        DATA_DIR, args.type, args.name,
        owner=args.owner, scenario_code=args.scenario,
    )
    if args.authorized_by:
        meta = lifecycle.start_exercise(DATA_DIR, meta["id"],
                                        authorized_by=args.authorized_by)
    print(json.dumps(meta, indent=2, ensure_ascii=False))


def cmd_status(args):
    lifecycle.check_timeouts(DATA_DIR)
    ejercicios = lifecycle.list_exercises(DATA_DIR)
    if not ejercicios:
        print("Sin ejercicios registrados.")
        return
    for m in ejercicios:
        print(f"{m['id']}  {m['status']:9}  {m['type']:13}  "
              f"{m['name']}  (autorizado por: {m.get('authorized_by') or '-'})")


def cmd_stop(args):
    meta = lifecycle.stop_exercise(DATA_DIR, args.id)
    print(f"Ejercicio {meta['id']} detenido ({meta['status']}).")


def cmd_report(args):
    meta = lifecycle.load_metadata(DATA_DIR, args.id)
    eventos = []
    log_path = ROOT / "data" / "exercises" / args.id / "logs" / "events.log"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                eventos.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    contenido = generate_report({**meta, "_dir": str(log_path.parent.parent)},
                                eventos=eventos)
    out = save_report(DATA_DIR, args.id, contenido)
    print(f"Reporte generado: {out}")


def main():
    parser = argparse.ArgumentParser(description="CLI de ejercicios SOP")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start", help="Crear e iniciar ejercicio")
    p.add_argument("--type", required=True,
                   choices=lifecycle.EXERCISE_TYPES)
    p.add_argument("--name", required=True)
    p.add_argument("--scenario", default=None)
    p.add_argument("--owner", default=None)
    p.add_argument("--authorized-by", dest="authorized_by", default=None)
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("status", help="Listar ejercicios")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("stop", help="Detener ejercicio")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("report", help="Generar reporte")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, PermissionError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
