<p align="center">
  <img src="docs/logo.png" alt="OpenUDI" width="280" />
</p>

<h1 align="center">br_accUDI</h1>

<p align="center">
  <strong>Infraestrutura open-source de grafo que cruza dados públicos municipais de Uberlândia para gerar inteligência cívica acionável.</strong>
</p>

<p align="center">
  Inspirado no <a href="https://github.com/World-Open-Graph/br-acc">br/acc</a>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="License: AGPL v3" /></a>
  <img src="https://img.shields.io/badge/Neo4j-5_Community-008CC1?logo=neo4j" alt="Neo4j" />
  <img src="https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react" alt="React" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker" alt="Docker" />
</p>

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

7 algoritmos determinísticos (sem IA/LLM) que cruzam o grafo em busca de irregularidades:

| # | Padrão | Descrição |
|---|--------|-----------|
| 1 | Empresa sancionada com contrato | Empresa no CEIS que venceu licitação durante sanção |
| 2 | Fracionamento de contratos | Multiplos contratos < R$ 80k para mesmo fornecedor no mesmo mês |
| 3 | Doador de campanha → contrato | Empresa doou para candidato e depois venceu contratos públicos |
| 4 | Parente de PEP com contrato | Familiar de político é sócio de empresa com contrato público |
| 5 | Isenção fiscal + contrato | Empresa com isenção tributária que também venceu licitações |
| 6 | Devedor com contrato | Empresa em dívida ativa que venceu licitações |
| 7 | Incentivo cultural cruzado | PEP proponente de projeto cultural incentivado por empresa vinculada |

## Créditos

Este projeto foi inspirado e é um tributado ao trabalho do [br/acc (Brazilian Accelerationism)](https://github.com/World-Open-Graph/br-acc), criado por [Bruno César](https://github.com/brunocesarr) e mantido pela comunidade [World Open Graph](https://github.com/World-Open-Graph). A ideia de cruzar dados públicos em grafo para gerar inteligência cívica nasceu lá. O br_accUDI adapta esse conceito para o contexto municipal de Uberlândia (MG), com stack e implementação independentes.

## Legal

Todos os dados processados são públicos por lei. Base legal: LAI (Lei 12.527/2011), LC 131/2009, LGPD Art. 7 IV/VII, Lei 14.129/2021.

## Licença

[GNU Affero General Public License v3.0](LICENSE)
