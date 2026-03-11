# Phase 1: Foundation — Infrastructure + ETL Framework

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the OpenUDI project with Docker infrastructure, Neo4j schema, ETL framework, and the first working pipeline (CNPJ) that loads real company data from Uberlândia into the graph.

**Architecture:** Docker Compose orchestrates Neo4j + API + Frontend + ETL. The ETL framework uses a Pipeline ABC with extract/transform/load phases and a Neo4jBatchLoader for efficient batch writes. The API is a minimal FastAPI health endpoint. Frontend is a Vite stub.

**Tech Stack:** Python 3.12, FastAPI, Neo4j 5, React 19, Vite 6, TypeScript, Docker Compose, pandas, httpx

**Project root:** `/Users/viniciusmarques/Desktop/codigos/Projetos Vinicius/br_accUDI`

---

## Chunk 1: Project Scaffold + Docker Infrastructure

### Task 1: Git init + project root files

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `LICENSE`

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI
git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/

# Node
node_modules/
frontend/dist/

# Data
data/
*.csv
*.zip

# Environment
.env

# Neo4j
neo4j-data/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Firecrawl
.firecrawl/

# Audit
audit-results/
```

- [ ] **Step 3: Create .env.example**

```env
# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=openudi-dev-2026
NEO4J_DATABASE=neo4j
NEO4J_HEAP=512m
NEO4J_PAGECACHE=512m

# API
JWT_SECRET_KEY=change-me-in-production-min-32-chars!!
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
LOG_LEVEL=info
APP_ENV=dev
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_ANON=60/minute
RATE_LIMIT_AUTH=300/minute

# Feature flags
PRODUCT_TIER=community
PATTERNS_ENABLED=false
PUBLIC_MODE=true
PUBLIC_ALLOW_PERSON=false
PUBLIC_ALLOW_ENTITY_LOOKUP=false

# Pattern thresholds
PATTERN_SPLIT_THRESHOLD_VALUE=80000.0
PATTERN_SPLIT_MIN_COUNT=3
PATTERN_SHARE_THRESHOLD=0.6
PATTERN_MAX_EVIDENCE_REFS=50

# Frontend
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_MODE=true
VITE_PATTERNS_ENABLED=false

# Municipality
CITY_NAME=Uberlândia
CITY_CODE=3170206
CITY_UF=MG
```

- [ ] **Step 4: Create LICENSE (AGPL v3)**

Download AGPL v3 text or copy from br-acc.

- [ ] **Step 5: Create README.md**

```markdown
# br_accUDI

Open-source graph infrastructure that cross-references public databases from Uberlândia to generate actionable civic intelligence.

Inspired by [br/acc](https://github.com/World-Open-Graph/br-acc).

## Quick Start

\`\`\`bash
cp .env.example .env
docker compose up -d --build
make seed
\`\`\`

- API: http://localhost:8000/health
- Frontend: http://localhost:3000
- Neo4j Browser: http://localhost:7474

## License

AGPL v3
```

- [ ] **Step 6: Initial commit**

```bash
git add .gitignore .env.example README.md LICENSE docs/
git commit -m "chore: init project with scaffold and design docs"
```

---

### Task 2: Docker Compose + Dockerfile

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
services:
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: "${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-openudi-dev-2026}"
      NEO4J_server_memory_heap_initial__size: "${NEO4J_HEAP:-512m}"
      NEO4J_server_memory_heap_max__size: "${NEO4J_HEAP:-512m}"
      NEO4J_server_memory_pagecache_size: "${NEO4J_PAGECACHE:-512m}"
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: "apoc.*"
    volumes:
      - neo4j-data:/data
      - ./infra/neo4j/init.cypher:/var/lib/neo4j/import/init.cypher:ro
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD:-openudi-dev-2026}", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 10

  api:
    build:
      context: .
      target: api
    ports:
      - "8000:8000"
    environment:
      NEO4J_URI: "bolt://neo4j:7687"
      NEO4J_USER: "${NEO4J_USER:-neo4j}"
      NEO4J_PASSWORD: "${NEO4J_PASSWORD:-openudi-dev-2026}"
      NEO4J_DATABASE: "${NEO4J_DATABASE:-neo4j}"
      JWT_SECRET_KEY: "${JWT_SECRET_KEY:-change-me-in-production-min-32-chars!!}"
      APP_ENV: "${APP_ENV:-dev}"
      LOG_LEVEL: "${LOG_LEVEL:-info}"
      CORS_ORIGINS: "${CORS_ORIGINS:-http://localhost:3000}"
      PATTERNS_ENABLED: "${PATTERNS_ENABLED:-false}"
      PUBLIC_MODE: "${PUBLIC_MODE:-true}"
    depends_on:
      neo4j:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: .
      target: frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: "${VITE_API_URL:-http://localhost:8000}"
      VITE_PUBLIC_MODE: "${VITE_PUBLIC_MODE:-true}"
    depends_on:
      api:
        condition: service_healthy

  etl:
    build:
      context: .
      target: etl
    profiles: ["etl"]
    environment:
      NEO4J_URI: "bolt://neo4j:7687"
      NEO4J_USER: "${NEO4J_USER:-neo4j}"
      NEO4J_PASSWORD: "${NEO4J_PASSWORD:-openudi-dev-2026}"
      NEO4J_DATABASE: "${NEO4J_DATABASE:-neo4j}"
    volumes:
      - .:/workspace
    working_dir: /workspace
    depends_on:
      neo4j:
        condition: service_healthy

volumes:
  neo4j-data:
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
# ── API ──────────────────────────────────────────
FROM python:3.12-slim AS api

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/src/ ./src/

CMD ["uvicorn", "openudi.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Frontend build ───────────────────────────────
FROM node:22-slim AS frontend-build

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Frontend serve ───────────────────────────────
FROM nginx:alpine AS frontend

COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY infra/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]

# ── ETL ──────────────────────────────────────────
FROM python:3.12-slim AS etl

WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

- [ ] **Step 3: Create nginx config**

Create `infra/nginx/default.conf`:

```nginx
server {
    listen 3000;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml Dockerfile infra/nginx/default.conf
git commit -m "infra: add Docker Compose stack with Neo4j, API, Frontend, ETL"
```

---

### Task 3: Neo4j schema + seed data

**Files:**
- Create: `infra/neo4j/init.cypher`
- Create: `infra/scripts/seed-dev.cypher`
- Create: `infra/scripts/seed-dev.sh`

- [ ] **Step 1: Create Neo4j schema (init.cypher)**

```cypher
// ── Uniqueness constraints ──────────────────────
CREATE CONSTRAINT person_cpf IF NOT EXISTS FOR (n:Person) REQUIRE n.cpf IS UNIQUE;
CREATE CONSTRAINT company_cnpj IF NOT EXISTS FOR (n:Company) REQUIRE n.cnpj IS UNIQUE;
CREATE CONSTRAINT contract_id IF NOT EXISTS FOR (n:Contract) REQUIRE n.contract_id IS UNIQUE;
CREATE CONSTRAINT sanction_id IF NOT EXISTS FOR (n:Sanction) REQUIRE n.sanction_id IS UNIQUE;
CREATE CONSTRAINT amendment_id IF NOT EXISTS FOR (n:Amendment) REQUIRE n.amendment_id IS UNIQUE;
CREATE CONSTRAINT public_office_id IF NOT EXISTS FOR (n:PublicOffice) REQUIRE n.office_id IS UNIQUE;
CREATE CONSTRAINT tax_debt_id IF NOT EXISTS FOR (n:TaxDebt) REQUIRE n.debt_id IS UNIQUE;
CREATE CONSTRAINT tax_waiver_id IF NOT EXISTS FOR (n:TaxWaiver) REQUIRE n.waiver_id IS UNIQUE;
CREATE CONSTRAINT cultural_incentive_id IF NOT EXISTS FOR (n:CulturalIncentive) REQUIRE n.incentive_id IS UNIQUE;
CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (n:Transfer) REQUIRE n.transfer_id IS UNIQUE;
CREATE CONSTRAINT partner_id IF NOT EXISTS FOR (n:Partner) REQUIRE n.partner_id IS UNIQUE;
CREATE CONSTRAINT ingestion_run_id IF NOT EXISTS FOR (n:IngestionRun) REQUIRE n.run_id IS UNIQUE;

// ── Indexes ─────────────────────────────────────
CREATE INDEX person_name IF NOT EXISTS FOR (n:Person) ON (n.name);
CREATE INDEX company_razao IF NOT EXISTS FOR (n:Company) ON (n.razao_social);
CREATE INDEX company_municipio IF NOT EXISTS FOR (n:Company) ON (n.municipio);
CREATE INDEX contract_value IF NOT EXISTS FOR (n:Contract) ON (n.value);
CREATE INDEX contract_date IF NOT EXISTS FOR (n:Contract) ON (n.date);
CREATE INDEX contract_org IF NOT EXISTS FOR (n:Contract) ON (n.contracting_org);

// ── Full-text search index ──────────────────────
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
FOR (n:Person|Company|Contract|Sanction|Amendment|TaxDebt|TaxWaiver|CulturalIncentive|Transfer)
ON EACH [n.name, n.razao_social, n.cpf, n.cnpj, n.object, n.contracting_org];
```

- [ ] **Step 2: Create seed data (seed-dev.cypher)**

```cypher
// ── Synthetic seed data for OpenUDI development ─
// All data is fictional. CPFs/CNPJs are invalid test values.

// Persons (fictional politicians + family)
MERGE (p1:Person {cpf: '11111111111'}) SET p1.name = 'CARLOS SILVA NETO', p1.is_pep = true, p1.cargo = 'Vereador', p1.municipio = 'UBERLANDIA', p1.uf = 'MG', p1.patrimonio_declarado = 350000.00;
MERGE (p2:Person {cpf: '22222222222'}) SET p2.name = 'MARIA SILVA COSTA', p2.is_pep = false, p2.municipio = 'UBERLANDIA', p2.uf = 'MG';
MERGE (p3:Person {cpf: '33333333333'}) SET p3.name = 'JOAO OLIVEIRA SANTOS', p3.is_pep = true, p3.cargo = 'Prefeito', p3.municipio = 'UBERLANDIA', p3.uf = 'MG', p3.patrimonio_declarado = 1200000.00;
MERGE (p4:Person {cpf: '44444444444'}) SET p4.name = 'ANA OLIVEIRA LIMA', p4.is_pep = false, p4.municipio = 'UBERLANDIA', p4.uf = 'MG';
MERGE (p5:Person {cpf: '55555555555'}) SET p5.name = 'PEDRO MENDES JUNIOR', p5.is_pep = true, p5.cargo = 'Vereador', p5.municipio = 'UBERLANDIA', p5.uf = 'MG', p5.patrimonio_declarado = 180000.00;

// Family relationships
MERGE (p1)-[:CONJUGE_DE]->(p2);
MERGE (p3)-[:CONJUGE_DE]->(p4);
MERGE (p1)-[:PARENTE_DE {grau: 'irmao'}]->(p5);

// Companies (fictional, Uberlândia)
MERGE (c1:Company {cnpj: '11111111000100'}) SET c1.razao_social = 'SILVA CONSTRUCOES LTDA', c1.cnae_principal = '4120400', c1.capital_social = 500000.00, c1.municipio = 'UBERLANDIA', c1.uf = 'MG', c1.situacao = 'ATIVA';
MERGE (c2:Company {cnpj: '22222222000100'}) SET c2.razao_social = 'OLIVEIRA SERVICOS SA', c2.cnae_principal = '8121400', c2.capital_social = 200000.00, c2.municipio = 'UBERLANDIA', c2.uf = 'MG', c2.situacao = 'ATIVA';
MERGE (c3:Company {cnpj: '33333333000100'}) SET c3.razao_social = 'TECH SOLUTIONS UDI LTDA', c3.cnae_principal = '6201501', c3.capital_social = 100000.00, c3.municipio = 'UBERLANDIA', c3.uf = 'MG', c3.situacao = 'ATIVA';
MERGE (c4:Company {cnpj: '44444444000100'}) SET c4.razao_social = 'MENDES TRANSPORTES LTDA', c4.cnae_principal = '4930202', c4.capital_social = 300000.00, c4.municipio = 'UBERLANDIA', c4.uf = 'MG', c4.situacao = 'ATIVA';
MERGE (c5:Company {cnpj: '55555555000100'}) SET c5.razao_social = 'COSTA ALIMENTOS EIRELI', c5.cnae_principal = '5611201', c5.capital_social = 80000.00, c5.municipio = 'UBERLANDIA', c5.uf = 'MG', c5.situacao = 'ATIVA';

// Partnerships (spouse/family own companies)
MERGE (p2)-[:SOCIO_DE {qualificacao: 'Sócio-Administrador', data_entrada: '2018-03-15'}]->(c1);
MERGE (p4)-[:SOCIO_DE {qualificacao: 'Sócio-Administrador', data_entrada: '2019-06-20'}]->(c2);
MERGE (p5)-[:SOCIO_DE {qualificacao: 'Sócio', data_entrada: '2020-01-10'}]->(c4);
MERGE (p1)-[:SOCIO_DE {qualificacao: 'Sócio', data_entrada: '2017-08-01'}]->(c3);

// Contracts (municipal)
MERGE (ct1:Contract {contract_id: 'CTR-UDI-001'}) SET ct1.object = 'Reforma de escola municipal', ct1.value = 450000.00, ct1.contracting_org = 'Secretaria de Educacao', ct1.date = '2025-03-15', ct1.municipio = 'UBERLANDIA', ct1.modalidade = 'Pregao Eletronico';
MERGE (ct2:Contract {contract_id: 'CTR-UDI-002'}) SET ct2.object = 'Servico de limpeza urbana', ct2.value = 780000.00, ct2.contracting_org = 'Secretaria de Obras', ct2.date = '2025-05-20', ct2.municipio = 'UBERLANDIA', ct2.modalidade = 'Concorrencia';
MERGE (ct3:Contract {contract_id: 'CTR-UDI-003'}) SET ct3.object = 'Fornecimento de software', ct3.value = 65000.00, ct3.contracting_org = 'Prodaub', ct3.date = '2025-06-10', ct3.municipio = 'UBERLANDIA', ct3.modalidade = 'Dispensa';
MERGE (ct4:Contract {contract_id: 'CTR-UDI-004'}) SET ct4.object = 'Transporte escolar', ct4.value = 320000.00, ct4.contracting_org = 'Secretaria de Educacao', ct4.date = '2025-07-01', ct4.municipio = 'UBERLANDIA', ct4.modalidade = 'Pregao Eletronico';
MERGE (ct5:Contract {contract_id: 'CTR-UDI-005'}) SET ct5.object = 'Fornecimento de merenda', ct5.value = 75000.00, ct5.contracting_org = 'Secretaria de Educacao', ct5.date = '2025-07-15', ct5.municipio = 'UBERLANDIA', ct5.modalidade = 'Dispensa';

// Split contracts pattern (3x below R$ 80k same org/month)
MERGE (ct6:Contract {contract_id: 'CTR-UDI-006'}) SET ct6.object = 'Material de escritorio lote 1', ct6.value = 72000.00, ct6.contracting_org = 'Secretaria de Administracao', ct6.date = '2025-08-05', ct6.municipio = 'UBERLANDIA', ct6.modalidade = 'Dispensa';
MERGE (ct7:Contract {contract_id: 'CTR-UDI-007'}) SET ct7.object = 'Material de escritorio lote 2', ct7.value = 68000.00, ct7.contracting_org = 'Secretaria de Administracao', ct7.date = '2025-08-12', ct7.municipio = 'UBERLANDIA', ct7.modalidade = 'Dispensa';
MERGE (ct8:Contract {contract_id: 'CTR-UDI-008'}) SET ct8.object = 'Material de escritorio lote 3', ct8.value = 71000.00, ct8.contracting_org = 'Secretaria de Administracao', ct8.date = '2025-08-18', ct8.municipio = 'UBERLANDIA', ct8.modalidade = 'Dispensa';

// Contract wins (companies → contracts)
MERGE (c1)-[:VENCEU]->(ct1);
MERGE (c2)-[:VENCEU]->(ct2);
MERGE (c3)-[:VENCEU]->(ct3);
MERGE (c4)-[:VENCEU]->(ct4);
MERGE (c5)-[:VENCEU]->(ct5);
MERGE (c3)-[:VENCEU]->(ct6);
MERGE (c3)-[:VENCEU]->(ct7);
MERGE (c3)-[:VENCEU]->(ct8);

// Sanction
MERGE (s1:Sanction {sanction_id: 'CEIS-UDI-001'}) SET s1.type = 'CEIS', s1.reason = 'Fraude em licitacao', s1.date_start = '2024-01-15', s1.date_end = '2027-01-15', s1.source = 'CGU';
MERGE (c2)-[:SANCIONADA]->(s1);

// Tax debt (municipal)
MERGE (d1:TaxDebt {debt_id: 'DA-UDI-001'}) SET d1.tipo_divida = 'ISS', d1.valor_base = 125000.00, d1.valor_atualizado = 148000.00, d1.ano_vencimento = 2023;
MERGE (c4)-[:DEVEDOR]->(d1);

// Tax waiver (IPTU exemption)
MERGE (w1:TaxWaiver {waiver_id: 'REN-UDI-001'}) SET w1.tipo = 'Isencao IPTU', w1.legislacao = 'Lei 12345/2020', w1.ano = 2024, w1.valor_renunciado = 45000.00;
MERGE (c1)-[:BENEFICIARIO_ISENCAO]->(w1);

// Amendment
MERGE (a1:Amendment {amendment_id: 'EMD-UDI-001'}) SET a1.type = 'Individual', a1.function = 'Educacao', a1.value_committed = 500000.00, a1.value_paid = 350000.00, a1.year = 2025;
MERGE (p1)-[:AUTOR_EMENDA]->(a1);
MERGE (c1)-[:RECEBEU_EMENDA]->(a1);

// Elections
MERGE (e1:PublicOffice {office_id: 'ELEC-UDI-2024-001'}) SET e1.year = 2024, e1.cargo = 'Vereador', e1.municipio = 'UBERLANDIA', e1.uf = 'MG', e1.situacao = 'Eleito';
MERGE (p1)-[:CANDIDATO]->(e1);

// Campaign donation (donation-contract loop pattern)
MERGE (c3)-[:DOOU_PARA {valor: 50000.00, ano: 2024}]->(e1);

// Cultural incentive
MERGE (ci1:CulturalIncentive {incentive_id: 'CULT-UDI-001'}) SET ci1.projeto = 'Festival Cultural do Triangulo', ci1.area = 'Musica', ci1.valor_aprovado = 200000.00, ci1.valor_captado = 180000.00, ci1.ano = 2025, ci1.status = 'Realizado';
MERGE (p5)-[:PROPONENTE]->(ci1);
MERGE (c4)-[:INCENTIVADORA {valor: 80000.00, incentivo: 'ISS'}]->(ci1);

// Transfer
MERGE (t1:Transfer {transfer_id: 'TRANSF-UDI-001'}) SET t1.tipo = 'Fundo a Fundo', t1.valor = 2500000.00, t1.programa = 'PAB Fixo', t1.ano = 2025, t1.orgao_superior = 'Ministerio da Saude';

// Patterns exercised in this seed:
// 1. Sancionada com contrato: c2 sancionada + venceu ct2
// 2. Fracionamento: c3 venceu ct6+ct7+ct8 (mesmo mes, < R$80k)
// 3. Doador → contrato: c3 doou pra p1 + venceu ct3/ct6/ct7/ct8
// 4. Parente com contrato: p1 (vereador) conjuge p2 (socia c1) + c1 venceu ct1
// 5. Isenção + contrato: c1 beneficiaria isencao + venceu ct1
// 6. Devedor com contrato: c4 devedora + venceu ct4
// 7. Incentivo cultural cruzado: p5 (vereador/irmao p1) proponente + c4 incentivadora
```

- [ ] **Step 3: Create seed script (seed-dev.sh)**

```bash
#!/usr/bin/env bash
set -euo pipefail

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-openudi-dev-2026}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Loading schema..."
if command -v cypher-shell &>/dev/null; then
  cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" -f "$SCRIPT_DIR/../neo4j/init.cypher"
  echo "==> Loading seed data..."
  cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" -f "$SCRIPT_DIR/seed-dev.cypher"
elif docker ps --format '{{.Names}}' | grep -q 'neo4j'; then
  CONTAINER=$(docker ps --format '{{.Names}}' | grep 'neo4j' | head -1)
  echo "Using container: $CONTAINER"
  docker exec -i "$CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < "$SCRIPT_DIR/../neo4j/init.cypher"
  echo "==> Loading seed data..."
  docker exec -i "$CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < "$SCRIPT_DIR/seed-dev.cypher"
else
  echo "ERROR: cypher-shell not found and no Neo4j container running"
  exit 1
fi

echo "==> Seed complete!"
```

- [ ] **Step 4: Commit**

```bash
git add infra/
git commit -m "infra: add Neo4j schema, seed data with 7 test patterns, and seed script"
```

---

### Task 4: Makefile

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Create Makefile**

```makefile
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
download-cnpj: ## Download CNPJ data from Receita Federal
	cd etl && python -m openudi_etl.scripts.download_cnpj --data-dir ../data

etl-cnpj: ## Run CNPJ pipeline
	cd etl && python -m openudi_etl.runner cnpj --neo4j-password $${NEO4J_PASSWORD:-openudi-dev-2026} --data-dir ../data

bootstrap: ## Run all ETL pipelines (heavy)
	cd etl && python -m openudi_etl.runner all --neo4j-password $${NEO4J_PASSWORD:-openudi-dev-2026} --data-dir ../data

# ── Quality ─────────────────────────────────────
lint: ## Run linters
	cd api && ruff check src/ tests/
	cd etl && ruff check src/ tests/

test-api: ## Run API tests
	cd api && pytest tests/ -v

test-etl: ## Run ETL tests
	cd etl && pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-api test-etl test-frontend ## Run all tests

check: lint test ## Run linters + tests

# ── Cleanup ─────────────────────────────────────
clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
```

- [ ] **Step 2: Commit**

```bash
git add Makefile
git commit -m "chore: add Makefile with dev, seed, etl, quality targets"
```

---

## Chunk 2: API Foundation

### Task 5: Minimal FastAPI app

**Files:**
- Create: `api/requirements.txt`
- Create: `api/src/openudi/__init__.py`
- Create: `api/src/openudi/main.py`
- Create: `api/src/openudi/config.py`
- Create: `api/tests/__init__.py`
- Create: `api/tests/test_health.py`

- [ ] **Step 1: Create api/requirements.txt**

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
neo4j>=5.25.0
pydantic>=2.10.0
pydantic-settings>=2.7.0
slowapi>=0.1.9
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.28.0
ruff>=0.8.0
pytest>=8.3.0
pytest-asyncio>=0.25.0
```

- [ ] **Step 2: Write failing test**

Create `api/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from openudi.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI/api
pip install -r requirements.txt
PYTHONPATH=src pytest tests/test_health.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 4: Create config.py**

```python
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "openudi-dev-2026"
    neo4j_database: str = "neo4j"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"
    app_env: str = "dev"

    # Auth
    jwt_secret_key: str = "change-me-in-production-min-32-chars!!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    rate_limit_anon: str = "60/minute"
    rate_limit_auth: str = "300/minute"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Feature flags
    product_tier: str = "community"
    patterns_enabled: bool = False
    public_mode: bool = True
    public_allow_person: bool = False
    public_allow_entity_lookup: bool = False

    # Pattern thresholds
    pattern_split_threshold_value: float = 80000.0
    pattern_split_min_count: int = 3
    pattern_share_threshold: float = 0.6
    pattern_max_evidence_refs: int = 50

    # Municipality
    city_name: str = "Uberlândia"
    city_code: str = "3170206"
    city_uf: str = "MG"

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
```

- [ ] **Step 5: Create main.py**

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from openudi.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: future Neo4j driver init goes here
    yield
    # Shutdown: future Neo4j driver close goes here


app = FastAPI(
    title="OpenUDI API",
    description="Uberlândia public data graph analysis tool",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 6: Create __init__.py files**

Create empty `api/src/openudi/__init__.py` and `api/tests/__init__.py`.

- [ ] **Step 7: Run test to verify it passes**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI/api
PYTHONPATH=src pytest tests/test_health.py -v
```

Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add api/
git commit -m "feat(api): add FastAPI app with health endpoint and config"
```

---

## Chunk 3: ETL Framework

### Task 6: Pipeline ABC + Neo4jBatchLoader

**Files:**
- Create: `etl/requirements.txt`
- Create: `etl/src/openudi_etl/__init__.py`
- Create: `etl/src/openudi_etl/base.py`
- Create: `etl/src/openudi_etl/loader.py`
- Create: `etl/tests/__init__.py`
- Create: `etl/tests/test_loader.py`

- [ ] **Step 1: Create etl/requirements.txt**

```
neo4j>=5.25.0
pandas>=2.2.0
httpx>=0.28.0
ruff>=0.8.0
pytest>=8.3.0
```

- [ ] **Step 2: Write failing test for loader**

Create `etl/tests/test_loader.py`:

```python
from unittest.mock import MagicMock

from openudi_etl.loader import Neo4jBatchLoader


def test_load_nodes_builds_correct_query():
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
    mock_session.run.return_value.consume.return_value.counters.nodes_created = 2

    loader = Neo4jBatchLoader(driver=mock_driver, batch_size=100)

    rows = [
        {"cnpj": "11111111000100", "razao_social": "EMPRESA A"},
        {"cnpj": "22222222000100", "razao_social": "EMPRESA B"},
    ]

    count = loader.load_nodes(label="Company", rows=rows, key_field="cnpj")
    assert count == 2
    assert mock_session.run.called


def test_load_nodes_skips_null_keys():
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
    mock_session.run.return_value.consume.return_value.counters.nodes_created = 1

    loader = Neo4jBatchLoader(driver=mock_driver, batch_size=100)

    rows = [
        {"cnpj": "11111111000100", "razao_social": "EMPRESA A"},
        {"cnpj": None, "razao_social": "EMPRESA SEM CNPJ"},
    ]

    count = loader.load_nodes(label="Company", rows=rows, key_field="cnpj")
    # Should only process 1 row (skip null key)
    call_args = mock_session.run.call_args
    assert len(call_args[1]["rows"]) == 1
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI/etl
pip install -r requirements.txt
PYTHONPATH=src pytest tests/test_loader.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 4: Create loader.py**

```python
from __future__ import annotations

import logging
import time

from neo4j import Driver
from neo4j.exceptions import TransientError

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


class Neo4jBatchLoader:
    def __init__(
        self,
        driver: Driver,
        batch_size: int = 10_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.batch_size = batch_size
        self.database = neo4j_database

    def load_nodes(
        self,
        label: str,
        rows: list[dict],
        key_field: str,
    ) -> int:
        rows = [r for r in rows if r.get(key_field) is not None]
        if not rows:
            return 0

        props = ", ".join(
            f"n.{k} = row.{k}" for k in rows[0] if k != key_field
        )
        query = (
            f"UNWIND $rows AS row "
            f"MERGE (n:{label} {{{key_field}: row.{key_field}}}) "
            f"SET {props}"
        )

        return self._run_batched(query, rows)

    def load_relationships(
        self,
        rel_type: str,
        rows: list[dict],
        source_label: str,
        source_key: str,
        target_label: str,
        target_key: str,
        properties: list[str] | None = None,
    ) -> int:
        if not rows:
            return 0

        prop_clause = ""
        if properties:
            prop_clause = ", ".join(f"r.{p} = row.{p}" for p in properties)
            prop_clause = f" SET {prop_clause}"

        query = (
            f"UNWIND $rows AS row "
            f"MATCH (a:{source_label} {{{source_key}: row.source_id}}) "
            f"MATCH (b:{target_label} {{{target_key}: row.target_id}}) "
            f"MERGE (a)-[r:{rel_type}]->(b)"
            f"{prop_clause}"
        )

        return self._run_batched(query, rows)

    def _run_batched(self, query: str, rows: list[dict]) -> int:
        total = 0
        for i in range(0, len(rows), self.batch_size):
            batch = rows[i : i + self.batch_size]
            total += self._run_with_retry(query, batch)
        return total

    def _run_with_retry(self, query: str, rows: list[dict]) -> int:
        for attempt in range(MAX_RETRIES):
            try:
                with self.driver.session(database=self.database) as session:
                    result = session.run(query, rows=rows)
                    counters = result.consume().counters
                    return (
                        counters.nodes_created
                        + counters.relationships_created
                        + counters.properties_set
                    )
            except TransientError:
                wait = 2**attempt
                logger.warning(
                    "TransientError on attempt %d, retrying in %ds",
                    attempt + 1,
                    wait,
                )
                time.sleep(wait)
        raise RuntimeError(f"Failed after {MAX_RETRIES} retries")
```

- [ ] **Step 5: Create base.py**

```python
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import uuid4

from neo4j import Driver

from openudi_etl.loader import Neo4jBatchLoader

logger = logging.getLogger(__name__)


class Pipeline(ABC):
    name: str = ""
    source_id: str = ""

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.data_dir = data_dir
        self.limit = limit
        self.chunk_size = chunk_size
        self.loader = Neo4jBatchLoader(
            driver=driver,
            batch_size=chunk_size,
            neo4j_database=neo4j_database,
        )
        self.database = neo4j_database
        self.rows_in = 0
        self.rows_loaded = 0

    @abstractmethod
    def extract(self) -> None: ...

    @abstractmethod
    def transform(self) -> None: ...

    @abstractmethod
    def load(self) -> None: ...

    def run(self) -> None:
        run_id = str(uuid4())
        started_at = datetime.now(timezone.utc).isoformat()

        self._upsert_ingestion_run(
            run_id=run_id,
            status="running",
            started_at=started_at,
        )

        try:
            logger.info("[%s] Extracting...", self.name)
            self.extract()
            logger.info("[%s] Transforming...", self.name)
            self.transform()
            logger.info("[%s] Loading...", self.name)
            self.load()

            self._upsert_ingestion_run(
                run_id=run_id,
                status="loaded",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                rows_in=self.rows_in,
                rows_loaded=self.rows_loaded,
            )
            logger.info(
                "[%s] Done: %d rows in, %d loaded",
                self.name,
                self.rows_in,
                self.rows_loaded,
            )
        except Exception as exc:
            self._upsert_ingestion_run(
                run_id=run_id,
                status="quality_fail",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                error=str(exc),
            )
            logger.exception("[%s] Failed: %s", self.name, exc)
            raise

    def _upsert_ingestion_run(
        self,
        run_id: str,
        status: str,
        started_at: str,
        finished_at: str | None = None,
        rows_in: int = 0,
        rows_loaded: int = 0,
        error: str | None = None,
    ) -> None:
        query = (
            "MERGE (r:IngestionRun {run_id: $run_id}) "
            "SET r.source_id = $source_id, "
            "    r.status = $status, "
            "    r.started_at = $started_at, "
            "    r.finished_at = $finished_at, "
            "    r.rows_in = $rows_in, "
            "    r.rows_loaded = $rows_loaded, "
            "    r.error = $error"
        )
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                run_id=run_id,
                source_id=self.source_id,
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                rows_in=rows_in,
                rows_loaded=rows_loaded,
                error=error,
            )
```

- [ ] **Step 6: Create __init__.py files**

Create empty `etl/src/openudi_etl/__init__.py` and `etl/tests/__init__.py`.

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI/etl
PYTHONPATH=src pytest tests/test_loader.py -v
```

Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add etl/
git commit -m "feat(etl): add Pipeline ABC and Neo4jBatchLoader with retry logic"
```

---

## Chunk 4: Frontend Stub

### Task 7: Vite + React stub with health check

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: Initialize frontend**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI/frontend
npm create vite@latest . -- --template react-ts
```

Select: React, TypeScript

- [ ] **Step 2: Install dependencies**

```bash
npm install react-router@7 zustand react-force-graph-2d lucide-react i18next react-i18next zod
npm install -D @types/react @types/react-dom vitest @testing-library/react
```

- [ ] **Step 3: Update vite.config.ts**

```typescript
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 4: Create minimal App.tsx**

```tsx
function App() {
  return (
    <div style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>br_accUDI</h1>
      <p>
        Open-source graph infrastructure for civic intelligence in Uberlandia.
      </p>
      <p>Coming soon.</p>
    </div>
  );
}

export default App;
```

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): add Vite + React 19 stub with proxy config"
```

---

## Chunk 5: Integration — Smoke Test

### Task 8: End-to-end smoke test

- [ ] **Step 1: Copy env and start stack**

```bash
cd /Users/viniciusmarques/Desktop/codigos/Projetos\ Vinicius/br_accUDI
cp .env.example .env
docker compose up -d --build
```

- [ ] **Step 2: Wait for healthy services, then seed**

```bash
docker compose ps  # verify all healthy
make seed
```

- [ ] **Step 3: Verify all endpoints**

```bash
# API health
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Neo4j (via browser)
# Open http://localhost:7474, run: MATCH (n) RETURN count(n)
# Expected: ~25 nodes from seed

# Frontend
# Open http://localhost:3000
# Expected: "br_accUDI" heading
```

- [ ] **Step 4: Verify seed patterns in Neo4j**

```bash
# Connect to Neo4j and run:
# MATCH (c:Company)-[:SANCIONADA]->(s:Sanction) RETURN c.razao_social, s.reason
# Expected: OLIVEIRA SERVICOS SA → Fraude em licitacao

# MATCH (c:Company)-[:VENCEU]->(ct:Contract) WHERE ct.value < 80000 RETURN c.razao_social, count(ct)
# Expected: TECH SOLUTIONS UDI LTDA → 3 (split contracts)
```

- [ ] **Step 5: Commit any fixes and tag**

```bash
git add -A
git commit -m "chore: integration smoke test verified"
git tag v0.1.0-foundation
```

---

## Summary

After completing this plan you will have:

1. **Docker stack** — Neo4j + API + Frontend + ETL, all orchestrated
2. **Neo4j schema** — 12 constraints, 6 indexes, full-text search
3. **Seed data** — 5 persons, 5 companies, 8 contracts, exercising all 7 patterns
4. **API** — FastAPI with health endpoint and config
5. **ETL framework** — Pipeline ABC + Neo4jBatchLoader with retry
6. **Frontend** — Vite + React stub
7. **Makefile** — dev, seed, etl, quality targets

**Next phase:** Phase 2 will add the first real ETL pipeline (CNPJ), search API endpoint, and frontend search page.
