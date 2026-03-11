from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from openudi.db import get_driver
from openudi.config import settings

router = APIRouter(prefix="/api/v1", tags=["patterns"])


class PatternResult(BaseModel):
    pattern_id: str
    pattern_name: str
    description: str
    risk_signal: int
    evidence: list[dict[str, Any]]


class PatternsResponse(BaseModel):
    patterns: list[PatternResult]


async def _detect_sanctioned_with_contract() -> PatternResult:
    """Pattern 1: Companies that won contracts while sanctioned."""
    driver = await get_driver()

    query = """
        MATCH (c:Company)-[:SANCIONADA]->(s:Sanction)
        MATCH (c)-[:VENCEU]->(ct:Contract)
        WHERE ct.date >= s.date_start
          AND (s.date_end IS NULL OR ct.date <= s.date_end)
        RETURN c.cnpj AS cnpj, c.razao_social AS company,
               s.reason AS sanction_reason, s.date_start AS sanction_start,
               ct.contract_id AS contract_id, ct.object AS contract_object,
               ct.value AS contract_value
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "cnpj": r["cnpj"],
            "company": r["company"],
            "sanction_reason": r["sanction_reason"],
            "sanction_start": r["sanction_start"],
            "contract_id": r["contract_id"],
            "contract_object": r["contract_object"],
            "contract_value": r["contract_value"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="sanctioned_with_contract",
        pattern_name="Empresa sancionada com contrato ativo",
        description=(
            "Empresas que venceram licitações durante o período "
            "em que estavam sancionadas."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_split_contracts() -> PatternResult:
    """Pattern 2: Potential contract splitting to avoid bidding thresholds."""
    driver = await get_driver()

    query = """
        MATCH (c:Company)-[:VENCEU]->(ct:Contract)
        WHERE ct.value < $threshold
        WITH c, ct, substring(ct.date, 0, 7) AS month, ct.contracting_org AS org
        WITH c, org, month,
             collect(ct) AS contracts,
             count(ct) AS cnt,
             sum(ct.value) AS total
        WHERE cnt >= $min_count
        RETURN c.cnpj AS cnpj, c.razao_social AS company,
               org, month, cnt AS contract_count, total AS total_value,
               [ct IN contracts | {
                   id: ct.contract_id,
                   object: ct.object,
                   value: ct.value
               }] AS contracts
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(
            query,
            threshold=settings.pattern_split_threshold_value,
            min_count=settings.pattern_split_min_count,
        )
        records = await result.data()

    evidence = [
        {
            "cnpj": r["cnpj"],
            "company": r["company"],
            "contracting_org": r["org"],
            "month": r["month"],
            "contract_count": r["contract_count"],
            "total_value": r["total_value"],
            "contracts": r["contracts"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="split_contracts",
        pattern_name="Possível fracionamento de contratos",
        description=(
            "Múltiplos contratos de baixo valor para o mesmo fornecedor "
            "no mesmo mês, indicando possível fracionamento para "
            "dispensar licitação."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_donor_got_contract() -> PatternResult:
    """Pattern 3: Campaign donors that later won government contracts."""
    driver = await get_driver()

    query = """
        MATCH (c:Company)-[:DOOU_PARA]->(e:PublicOffice)<-[:CANDIDATO]-(p:Person)
        MATCH (c)-[:VENCEU]->(ct:Contract)
        RETURN c.cnpj AS cnpj, c.razao_social AS company,
               p.name AS politician, e.cargo AS office,
               ct.contract_id AS contract_id, ct.object AS contract_object,
               ct.value AS contract_value
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "cnpj": r["cnpj"],
            "company": r["company"],
            "politician": r["politician"],
            "office": r["office"],
            "contract_id": r["contract_id"],
            "contract_object": r["contract_object"],
            "contract_value": r["contract_value"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="donor_got_contract",
        pattern_name="Doador de campanha com contrato público",
        description=(
            "Empresas que doaram para campanhas políticas e "
            "posteriormente venceram contratos públicos ligados "
            "ao cargo do candidato beneficiado."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_pep_relative_contract() -> PatternResult:
    """Pattern 4: PEP's relative is partner in company that won contracts."""
    driver = await get_driver()

    query = """
        MATCH (pep:Person {is_pep: true})-[:CONJUGE_DE|PARENTE_DE]-(parente:Person)
        MATCH (parente)-[:SOCIO_DE]->(c:Company)-[:VENCEU]->(ct:Contract)
        RETURN pep.name AS pep_name, pep.cargo AS pep_cargo,
               parente.name AS relative_name,
               c.cnpj AS cnpj, c.razao_social AS company,
               ct.contract_id AS contract_id, ct.object AS contract_object,
               ct.value AS contract_value
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "pep": r["pep_name"],
            "cargo": r["pep_cargo"],
            "relative": r["relative_name"],
            "cnpj": r["cnpj"],
            "company": r["company"],
            "contract_id": r["contract_id"],
            "contract_object": r["contract_object"],
            "contract_value": r["contract_value"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="pep_relative_contract",
        pattern_name="Parente de PEP com contrato público",
        description=(
            "Familiares de pessoas politicamente expostas são sócios "
            "de empresas que venceram contratos públicos municipais."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_tax_waiver_with_contract() -> PatternResult:
    """Pattern 5: Company with tax waiver that also won contracts."""
    driver = await get_driver()

    query = """
        MATCH (c:Company)-[:BENEFICIARIO_ISENCAO]->(w:TaxWaiver)
        MATCH (c)-[:VENCEU]->(ct:Contract)
        RETURN c.cnpj AS cnpj, c.razao_social AS company,
               w.tipo AS waiver_type, w.legislacao AS legislation,
               w.valor_renunciado AS waiver_value,
               ct.contract_id AS contract_id, ct.object AS contract_object,
               ct.value AS contract_value
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "cnpj": r["cnpj"],
            "company": r["company"],
            "waiver_type": r["waiver_type"],
            "legislation": r["legislation"],
            "waiver_value": r["waiver_value"],
            "contract_id": r["contract_id"],
            "contract_object": r["contract_object"],
            "contract_value": r["contract_value"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="tax_waiver_with_contract",
        pattern_name="Beneficiário de isenção fiscal com contrato",
        description=(
            "Empresas que recebem isenções ou benefícios fiscais "
            "do município e ao mesmo tempo vencem licitações públicas."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_debtor_with_contract() -> PatternResult:
    """Pattern 6: Company with active tax debt that won contracts."""
    driver = await get_driver()

    query = """
        MATCH (c:Company)-[:DEVEDOR]->(d:TaxDebt)
        MATCH (c)-[:VENCEU]->(ct:Contract)
        RETURN c.cnpj AS cnpj, c.razao_social AS company,
               d.tipo_divida AS debt_type,
               d.valor_atualizado AS debt_value,
               d.ano_vencimento AS debt_year,
               ct.contract_id AS contract_id, ct.object AS contract_object,
               ct.value AS contract_value
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "cnpj": r["cnpj"],
            "company": r["company"],
            "debt_type": r["debt_type"],
            "debt_value": r["debt_value"],
            "debt_year": r["debt_year"],
            "contract_id": r["contract_id"],
            "contract_object": r["contract_object"],
            "contract_value": r["contract_value"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="debtor_with_contract",
        pattern_name="Empresa devedora com contrato público",
        description=(
            "Empresas inscritas em dívida ativa municipal que "
            "venceram licitações públicas, indicando possível "
            "irregularidade na habilitação."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


async def _detect_cultural_incentive_crossover() -> PatternResult:
    """Pattern 7: PEP proposes cultural project + company they're linked to sponsors it."""
    driver = await get_driver()

    query = """
        MATCH (pep:Person {is_pep: true})-[:PROPONENTE]->(ci:CulturalIncentive)
        MATCH (c:Company)-[:INCENTIVADORA]->(ci)
        OPTIONAL MATCH (pep)-[:SOCIO_DE|PARENTE_DE|CONJUGE_DE*1..2]-(linked)-[:SOCIO_DE]->(c)
        RETURN pep.name AS pep_name, pep.cargo AS pep_cargo,
               ci.projeto AS project, ci.valor_aprovado AS approved_value,
               c.cnpj AS cnpj, c.razao_social AS company,
               linked.name AS linked_person
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query)
        records = await result.data()

    evidence = [
        {
            "pep": r["pep_name"],
            "cargo": r["pep_cargo"],
            "project": r["project"],
            "approved_value": r["approved_value"],
            "cnpj": r["cnpj"],
            "company": r["company"],
            "linked_person": r["linked_person"],
        }
        for r in records[: settings.pattern_max_evidence_refs]
    ]

    return PatternResult(
        pattern_id="cultural_incentive_crossover",
        pattern_name="Incentivo cultural com conexão política",
        description=(
            "Pessoa politicamente exposta é proponente de projeto cultural "
            "incentivado por empresa com a qual possui vínculo direto "
            "ou familiar."
        ),
        risk_signal=len(records),
        evidence=evidence,
    )


@router.get("/patterns", response_model=PatternsResponse)
async def get_patterns() -> PatternsResponse:
    """Return detected risk patterns from the graph data."""
    results = [
        await _detect_sanctioned_with_contract(),
        await _detect_split_contracts(),
        await _detect_donor_got_contract(),
        await _detect_pep_relative_contract(),
        await _detect_tax_waiver_with_contract(),
        await _detect_debtor_with_contract(),
        await _detect_cultural_incentive_crossover(),
    ]

    return PatternsResponse(patterns=results)
