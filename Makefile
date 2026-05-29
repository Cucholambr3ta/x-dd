# X-DD — Makefile unificado
# Hasta que se consolide en `xdd` CLI Python (ADR-0008, post-v0.1.0),
# este Makefile ofrece UX uniforme sobre los scripts existentes.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PY ?= python3

.PHONY: help doctor start init lint test pytest bats shield install trace cierre version

help: ## Lista los targets disponibles
	@echo "X-DD — comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Más info: ./README.md, ./INSTALL.md, ./DEPENDENCIES.md"

doctor: ## Verifica el entorno (deps, scripts, perfil del proyecto)
	@bash ./scripts/xdd-doctor.sh

start: ## Arranca X-DD (indexa MemPalace + lanza orquestador)
	@bash ./scripts/xdd-start.sh

init: ## Bootstrap de un proyecto nuevo (uso: make init DEST=/ruta/proyecto)
	@if [ -z "$(DEST)" ]; then \
		echo "Uso: make init DEST=/ruta/al/proyecto"; \
		exit 1; \
	fi
	@bash ./scripts/xdd-init.sh "$(DEST)"

lint: ## Lint de workflows X-DD
	@bash ./scripts/lint-workflows.sh

install: ## Instala dependencias de desarrollo (pytest, jsonschema)
	$(PY) -m pip install -r requirements-dev.txt
	@echo "[X-DD] Para bats: sudo apt install bats / brew install bats-core"

test: lint pytest bats shield ## Suite completa (lint + pytest + bats + AgentShield) — gate Art. 7 §4
	@echo "[X-DD] suite completa OK"

pytest: ## Tests Python (pytest)
	$(PY) -m pytest -q

bats: ## Tests shell (bats unit + e2e)
	@command -v bats >/dev/null || { echo "bats no instalado — make install"; exit 1; }
	bats tests/bats/ tests/e2e/

shield: ## AgentShield audit (falla si crit/high)
	$(PY) scripts/xdd-shield.py audit --severity=high

trace: ## Sincroniza Gantt y CHANGELOG (invocá /xdd-trace en el orquestador)
	@echo "[X-DD] Invocá '/xdd-trace' en Claude Code / OpenCode."
	@echo "       Edita PROJ-MASTER-PLAN.md y docs/CHANGELOG.md tras cerrar un sprint."

cierre: ## Cierre formal de fase (invocá /cierre-fase en el orquestador)
	@echo "[X-DD] Invocá '/cierre-fase' en Claude Code / OpenCode."
	@echo "       Actualiza memoria.md y lecciones.md."

version: ## Muestra la versión actual de X-DD (lee de PROJ-MASTER-PLAN.md o RELEASES/)
	@if [ -f "RELEASES/v0.1.0.md" ]; then \
		echo "X-DD v0.1.0"; \
	else \
		echo "X-DD pre-v0.1.0 (en desarrollo — ver PROJ-MASTER-PLAN.md)"; \
	fi
