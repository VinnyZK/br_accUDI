# br_accUDI

**Infraestrutura open-source de grafo que cruza dados públicos municipais de Uberlândia para gerar inteligência cívica acionável.**

Inspirado no [br/acc](https://github.com/World-Open-Graph/br-acc).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## Quick Start

```bash
cp .env.example .env
docker compose up -d --build
make seed
```

Verificar:

- API: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Neo4j Browser: http://localhost:7474

## Arquitetura

| Camada | Tecnologia |
|--------|-----------|
| Graph DB | Neo4j 5 Community |
| Backend | FastAPI (Python 3.12+, async) |
| Frontend | Vite + React 19 + TypeScript |
| ETL | Python (pandas, httpx) |
| Infra | Docker Compose |

```
api/          FastAPI backend (routes, services, models)
etl/          ETL pipelines and download scripts
frontend/     React app (Vite + TypeScript)
infra/        Docker, Neo4j schema, seed scripts
scripts/      Utility and automation scripts
docs/         Documentation, specs, plans
data/         Downloaded datasets (git-ignored)
```

## Fontes de Dados (v1)

1. Receita Federal (CNPJ) — empresas + sócios de Uberlândia
2. TSE — candidatos, doações, bens declarados
3. Portal Transparência Federal — transferências, convênios, emendas
4. CEIS/CNEP — sanções
5. Prefeitura — Dívida Ativa
6. Prefeitura — Receitas
7. Prefeitura — Incentivos Culturais
8. Prefeitura — Renúncias Fiscais
9. PNCP — licitações e contratos municipais
10. TCE-MG — despesas, licitações, folha do município

## Padrões Detectados

| # | Padrão |
|---|--------|
| 1 | Empresa sancionada com contrato ativo |
| 2 | Fracionamento de contratos (< R$ 80k) |
| 3 | Concentração de fornecedor (> 60%) |
| 4 | Devedor com contrato |
| 5 | Doador de campanha → contrato |
| 6 | Parente de político com contrato |
| 7 | Isenção fiscal + contrato |
| 8 | Incentivo cultural cruzado |

## Legal

Todos os dados processados são públicos por lei. Base legal: LAI (Lei 12.527/2011), LC 131/2009, LGPD Art. 7 IV/VII, Lei 14.129/2021.

## Licença

[GNU Affero General Public License v3.0](LICENSE)
