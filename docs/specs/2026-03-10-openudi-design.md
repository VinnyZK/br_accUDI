# OpenUDI — Design Spec

**Data:** 2026-03-10
**Status:** Aprovado

## Resumo

Infraestrutura open-source de grafo que cruza dados públicos municipais de Uberlândia para gerar inteligência cívica acionável. Projeto independente inspirado no br/acc, com foco 100% municipal.

## Decisões

- **Público:** Jornalistas, ativistas, estudantes, devs, professores
- **Posicionamento:** Projeto independente (não fork do br/acc)
- **Escopo:** Uberlândia apenas (v1)
- **Detecção de padrões:** Regras determinísticas puras (sem LLM)
- **Bootstrap:** Seed sintético + bootstrap com dados reais
- **Licença:** AGPL v3

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Graph DB | Neo4j 5 Community |
| Backend | FastAPI (Python 3.12+, async) |
| Frontend | Vite + React 19 + TypeScript |
| ETL | Python (pandas, httpx) |
| Infra | Docker Compose |

## Fontes de Dados (v1) — 10 Pipelines

### Existentes (adaptar do br/acc)
1. Receita Federal (CNPJ) — empresas + sócios de Uberlândia
2. TSE — candidatos, doações, bens declarados
3. Portal Transparência Federal — transferências, convênios, emendas
4. CEIS/CNEP — sanções

### Novos (municipais)
5. Prefeitura — Dívida Ativa (CPF/CNPJ devedores)
6. Prefeitura — Receitas (arrecadação por tipo)
7. Prefeitura — Incentivos Culturais (proponentes, empresas)
8. Prefeitura — Renúncias Fiscais (beneficiários isenção IPTU)
9. PNCP — licitações e contratos municipais (API REST)
10. TCE-MG — despesas, licitações, folha do município

## Modelagem do Grafo

### Nós
- `Company` (cnpj)
- `Person` (cpf)
- `Contract` (contract_id)
- `Sanction` (sanction_id)
- `Amendment` (amendment_id)
- `PublicOffice` (office_id)
- `TaxDebt` (debt_id)
- `TaxWaiver` (waiver_id)
- `CulturalIncentive` (incentive_id)
- `Transfer` (transfer_id)

### Relações
- `SOCIO_DE` (Person → Company)
- `PARENTE_DE` (Person → Person)
- `CONJUGE_DE` (Person → Person)
- `CONTRATADO` (Company → Contract)
- `CONTRATANTE` (Contract → órgão)
- `SANCIONADA` (Company → Sanction)
- `DOOU_PARA` (Company/Person → candidatura)
- `CANDIDATO` (Person → PublicOffice)
- `DEVEDOR` (Company/Person → TaxDebt)
- `BENEFICIARIO_ISENCAO` (Company/Person → TaxWaiver)
- `RECEBEU_EMENDA` (Company → Amendment)
- `PROPONENTE` (Person/Company → CulturalIncentive)
- `INCENTIVADORA` (Company → CulturalIncentive)

## Padrões Determinísticos (v1) — 8 Regras

1. **Sancionada com contrato** — empresa CEIS/CNEP recebendo contrato municipal
2. **Fracionamento de contratos** — múltiplos contratos (mesmo órgão, objeto, mês) < R$ 80k
3. **Concentração de fornecedor** — empresa com >60% do gasto de uma secretaria
4. **Devedor com contrato** — empresa com dívida ativa ganhando licitação
5. **Doador → contrato** — doador de campanha que depois ganhou contrato
6. **Parente de político com contrato** — sócio de empresa contratada é parente de vereador/prefeito
7. **Isenção fiscal + contrato** — empresa com isenção IPTU que também é fornecedora
8. **Incentivo cultural cruzado** — empresa incentivadora ligada a político

## Exposure Index (0-100)

- Conexões no grafo (25%)
- Variedade de fontes (25%)
- Volume financeiro (20%)
- Padrões detectados (20%)
- Comparação com pares (10%)

## Frontend

1. **Landing Page** — hero + stats + animação do grafo
2. **Busca** — search bar full-text → resultados
3. **Análise de Entidade** — grafo interativo + sidebar (conexões, timeline, score)
4. **Padrões** — alertas ordenados por risk signal com evidências
5. **Sobre** — metodologia, fontes, base legal

## Bootstrap

- `docker compose up` + `make seed` → dados sintéticos (segundos)
- `make bootstrap` → ETL completo com dados reais (minutos/horas)

## Compliance

- Dados 100% públicos por lei
- Base legal: LAI, LC 131/2009, LGPD Art. 7 IV/VII, Lei 14.129/2021
- Public-safe defaults: CPF mascarado, person lookup desabilitado
