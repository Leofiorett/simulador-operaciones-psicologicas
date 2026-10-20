# Simulador de Operaciones Psicológicas (SOP)
# Plataforma de instrucción OPSIC - audiencias sintéticas en red aislada

COMPOSE := docker compose
PROJECT_DIR := $(shell pwd)
DATA_DIR := $(PROJECT_DIR)/data
BACKUP_DIR := $(DATA_DIR)/backups
VENV := $(PROJECT_DIR)/.venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help setup deploy undeploy restart status validate health-check logs test \
        exercise-start exercise-status exercise-stop exercise-reset exercise-report \
        backup restore cleanup frontend-dev

help:
	@echo "Simulador de Operaciones Psicologicas (SOP)"
	@echo ""
	@echo "Setup:"
	@echo "  make setup           Instalar dependencias locales (venv, tests)"
	@echo "  sudo make deploy     Levantar servicios Docker"
	@echo "  make validate        Validar entorno"
	@echo "  make health-check    Salud de servicios"
	@echo ""
	@echo "Ejercicios:"
	@echo "  make exercise-start TYPE=doctrina|planificacion|simulacion|defensa NAME=\"titulo\""
	@echo "  make exercise-status"
	@echo "  make exercise-stop ID=ex-XXXX"
	@echo "  make exercise-report ID=ex-XXXX"
	@echo "  sudo make exercise-reset   (borra datos permanentemente)"
	@echo ""
	@echo "Operación:"
	@echo "  make status | make logs SERVICE=backend | make test | make backup"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-local.txt
	@echo "OK: venv listo. Ejecutando tests del motor..."
	$(VENV)/bin/python -m pytest tests/ -q

deploy:
	$(COMPOSE) up -d --build
	@sleep 5
	$(MAKE) health-check

undeploy:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart backend frontend

status:
	$(COMPOSE) ps

validate:
	@test -f docker-compose.yml || (echo "FALTA docker-compose.yml" && exit 1)
	@test -f services/backend/app/main.py || (echo "FALTA backend" && exit 1)
	@test -f src/simulation/engine.py || (echo "FALTA motor de simulacion" && exit 1)
	@test -f src/taxonomies/disarm_es.json || (echo "FALTA taxonomia DISARM-es" && exit 1)
	@ls src/curriculum/modulo-*.md >/dev/null 2>&1 || (echo "FALTAN modulos curriculares" && exit 1)
	@echo "VALIDACION OK: estructura completa"

health-check:
	@curl -sf http://localhost:8001/api/health >/dev/null && echo "backend: OK" || echo "backend: FALLO"
	@curl -sf http://localhost:8090/ >/dev/null && echo "frontend: OK" || echo "frontend: FALLO"
	@$(COMPOSE) exec -T db pg_isready -U sop -d sop >/dev/null && echo "db: OK" || echo "db: FALLO"
	@$(COMPOSE) exec -T redis redis-cli ping >/dev/null && echo "redis: OK" || echo "redis: FALLO"

logs:
	$(COMPOSE) logs -f --tail=100 $(SERVICE)

test:
	$(PYTHON) -m pytest tests/ -v

# ------------------- Ejercicios -------------------

exercise-start:
ifndef TYPE
	@echo "Uso: make exercise-start TYPE=doctrina|planificacion|simulacion|defensa NAME=\"titulo\""; exit 1
endif
	$(PYTHON) scripts/exercise_cli.py start --type "$(TYPE)" --name "$(NAME)"

exercise-status:
	$(PYTHON) scripts/exercise_cli.py status

exercise-stop:
ifndef ID
	@echo "Uso: make exercise-stop ID=ex-XXXX"; exit 1
endif
	$(PYTHON) scripts/exercise_cli.py stop --id "$(ID)"

exercise-report:
ifndef ID
	@echo "Uso: make exercise-report ID=ex-XXXX"; exit 1
endif
	$(PYTHON) scripts/exercise_cli.py report --id "$(ID)"

exercise-reset:
	@echo "ADVERTENCIA: esto borra TODOS los ejercicios y datos de forma PERMANENTE."
	@read -p "Escriba BORRAR para confirmar: " c && [ "$$c" = "BORRAR" ] || (echo "Cancelado."; exit 1)
	rm -rf $(DATA_DIR)/exercises/ex-* data/backups/*.old
	$(COMPOSE) restart backend
	@echo "Reset completado."

# ------------------- Backups / Limpieza -------------------

backup:
	@mkdir -p $(BACKUP_DIR)
	@ts=$$(date +%Y%m%d-%H%M%S); \
	$(COMPOSE) exec -T db pg_dump -U sop sop | gzip > $(BACKUP_DIR)/sop-db-$$ts.sql.gz; \
	tar czf $(BACKUP_DIR)/sop-exercises-$$ts.tar.gz $(DATA_DIR)/exercises; \
	echo "Backup creado: $$ts"

restore:
ifndef TS
	@echo "Uso: make restore TS=20260824-101500"; exit 1
endif
	gunzip -c $(BACKUP_DIR)/sop-db-$(TS).sql.gz | $(COMPOSE) exec -T db psql -U sop -d sop
	tar xzf $(BACKUP_DIR)/sop-exercises-$(TS).tar.gz -C /

cleanup:
	@find $(BACKUP_DIR) -name "*.gz" -mtime +30 -delete
	@find $(DATA_DIR)/exercises -maxdepth 1 -type d -name "ex-*" -mtime +90 -exec rm -rf {} \;
	@docker system prune -f
	@echo "Limpieza completada."

frontend-dev:
	cd services/frontend && npm install && npm run dev -- --host 0.0.0.0 --port 5199
