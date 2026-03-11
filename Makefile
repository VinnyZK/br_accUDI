.PHONY: help dev stop seed bootstrap clean lint test check

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Dev ─────────────────────────────────────────
setup-env: ## Copy .env.example to .env
	cp -n .env.example .env || true

dev: setup-env ## Start all services
	docker compose up -d --build

stop: ## Stop all services
	docker compose down

seed: ## Load schema + seed data into Neo4j
	bash infra/scripts/seed-dev.sh

# ── ETL ─────────────────────────────────────────
ETL_CMD = cd etl && PYTHONPATH=src python -m openudi_etl

download-cnpj: ## Download CNPJ data from Receita Federal
	$(ETL_CMD).scripts.download_cnpj --data-dir ../data

etl-cnpj: ## Run CNPJ pipeline (companies + partners)
	$(ETL_CMD).runner cnpj --data-dir ../data

etl-ceis: ## Run CEIS/CNEP pipeline (sanctions)
	$(ETL_CMD).runner ceis --data-dir ../data

etl-tse: ## Run TSE pipeline (candidates + elections)
	$(ETL_CMD).runner tse --data-dir ../data

etl-pncp: ## Run PNCP pipeline (public contracts)
	$(ETL_CMD).runner pncp --data-dir ../data

bootstrap: ## Run all ETL pipelines (heavy)
	$(ETL_CMD).runner all --data-dir ../data

# ── Quality ─────────────────────────────────────
lint: ## Run linters
	cd api && ruff check src/ tests/ || true
	cd etl && ruff check src/ tests/ || true

test-api: ## Run API tests
	cd api && PYTHONPATH=src pytest tests/ -v

test-etl: ## Run ETL tests
	cd etl && PYTHONPATH=src pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-api test-etl ## Run all tests

check: lint test ## Run linters + tests

# ── Cleanup ─────────────────────────────────────
clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
