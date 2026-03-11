"""PNCP Pipeline -- loads Contracts from Portal Nacional de Contratacoes Publicas.

Fetches public procurement data for Uberlandia (MG) from the PNCP API,
creates Contract nodes and VENCEU relationships (Company -> Contract)
when supplier CNPJ is available.
"""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta

import httpx

from openudi_etl.base import Pipeline

logger = logging.getLogger(__name__)

PNCP_BASE_URL = "https://pncp.gov.br/api/consulta/v1"
CONTRATACOES_URL = f"{PNCP_BASE_URL}/contratacoes/publicacao"
IBGE_UBERLANDIA = "3170206"

# PNCP procurement modality codes (codigoModalidadeContratacao)
# 1=Leilão, 2=Diálogo Competitivo, 3=Concurso, 4=Concorrência,
# 5=Pregão, 6=Dispensa, 7=Inexigibilidade, 8=Tomada de Preços,
# 9=Convite, 10=Concorrência Internacional, 11=Manifestação Interesse,
# 12=Pré-qualificação, 13=Credenciamento
MODALIDADES = list(range(1, 14))

# API page size (min 10, max 50)
PAGE_SIZE = 50

# Max date range per request (API limit: 365 days)
MAX_DATE_RANGE_DAYS = 365

# Number of years to look back
LOOKBACK_YEARS = 2

# Polite delay between API requests (seconds)
REQUEST_DELAY = 0.5

# Maximum retries per request
MAX_REQUEST_RETRIES = 3


def _fetch_page(
    client: httpx.Client,
    data_inicial: str,
    data_final: str,
    modalidade: int,
    pagina: int,
) -> dict:
    """Fetch a single page from the PNCP contratacoes endpoint."""
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoMunicipioIbge": IBGE_UBERLANDIA,
        "codigoModalidadeContratacao": modalidade,
        "pagina": pagina,
        "tamanhoPagina": PAGE_SIZE,
    }

    for attempt in range(MAX_REQUEST_RETRIES):
        try:
            resp = client.get(CONTRATACOES_URL, params=params, timeout=60)

            # No results: 204 No Content, 400, or 404
            if resp.status_code in (204, 400, 404):
                return {"data": []}

            # Server errors — retry
            if resp.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Server error {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )

            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            wait = 2 ** (attempt + 1)
            logger.warning(
                "PNCP request error (attempt %d/%d): %s — retrying in %ds",
                attempt + 1,
                MAX_REQUEST_RETRIES,
                exc,
                wait,
            )
            time.sleep(wait)

    # After all retries failed, return empty instead of crashing
    logger.warning(
        "PNCP API failed after %d retries (pagina=%d, mod=%d, %s–%s) — skipping",
        MAX_REQUEST_RETRIES, pagina, modalidade, data_inicial, data_final,
    )
    return {"data": []}


def _fetch_contract_items(
    client: httpx.Client,
    cnpj_orgao: str,
    ano: str,
    sequencial: str,
) -> list[dict]:
    """Fetch items/suppliers for a specific contract."""
    url = (
        f"{PNCP_BASE_URL}/contratacoes/"
        f"{cnpj_orgao}/{ano}/{sequencial}/itens"
    )
    try:
        resp = client.get(url, timeout=30)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json() if isinstance(resp.json(), list) else []
    except (httpx.HTTPStatusError, httpx.TransportError) as exc:
        logger.debug("Could not fetch items for %s/%s/%s: %s", cnpj_orgao, ano, sequencial, exc)
        return []


class PncpPipeline(Pipeline):
    name = "pncp"
    source_id = "pncp_contratacoes"

    def __init__(self, fetch_items: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._fetch_items = fetch_items

        # Intermediate data populated during extract/transform
        self._raw_contracts: list[dict] = []
        self._contracts: list[dict] = []
        self._venceu_rels: list[dict] = []

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    @staticmethod
    def _date_chunks(start: date, end: date) -> list[tuple[str, str]]:
        """Split a date range into chunks of at most MAX_DATE_RANGE_DAYS."""
        chunks: list[tuple[str, str]] = []
        cursor = start
        while cursor < end:
            chunk_end = min(cursor + timedelta(days=MAX_DATE_RANGE_DAYS - 1), end)
            chunks.append((
                cursor.strftime("%Y%m%d"),
                chunk_end.strftime("%Y%m%d"),
            ))
            cursor = chunk_end + timedelta(days=1)
        return chunks

    def extract(self) -> None:
        """Fetch all contracts for Uberlandia from PNCP."""
        today = date.today()
        start_date = today - timedelta(days=LOOKBACK_YEARS * 365)

        date_chunks = self._date_chunks(start_date, today)

        logger.info(
            "Fetching PNCP contracts for Uberlandia: %d date chunks × %d modalidades",
            len(date_chunks),
            len(MODALIDADES),
        )

        all_records: list[dict] = []
        hit_limit = False

        with httpx.Client(
            headers={"Accept": "application/json"},
            follow_redirects=True,
        ) as client:
            for data_inicial, data_final in date_chunks:
                if hit_limit:
                    break

                for modalidade in MODALIDADES:
                    if hit_limit:
                        break

                    pagina = 1
                    while True:
                        logger.info(
                            "  mod=%d  %s–%s  page %d ...",
                            modalidade, data_inicial, data_final, pagina,
                        )
                        try:
                            data = _fetch_page(
                                client, data_inicial, data_final,
                                modalidade, pagina,
                            )
                        except RuntimeError as exc:
                            logger.warning("Skipping: %s", exc)
                            break

                        if isinstance(data, list):
                            records = data
                        elif isinstance(data, dict):
                            records = data.get("data", data.get("content", []))
                            if not isinstance(records, list):
                                records = []
                        else:
                            records = []

                        if not records:
                            break

                        all_records.extend(records)

                        if self.limit and len(all_records) >= self.limit:
                            all_records = all_records[: self.limit]
                            hit_limit = True
                            break

                        if len(records) < PAGE_SIZE:
                            break

                        pagina += 1
                        time.sleep(REQUEST_DELAY)

                    time.sleep(REQUEST_DELAY)

            # Optionally fetch per-contract items to get supplier CNPJs
            if self._fetch_items:
                logger.info("Fetching contract items for %d contracts ...", len(all_records))
                for i, rec in enumerate(all_records):
                    cnpj_orgao = rec.get("orgaoEntidade", {}).get("cnpj", "")
                    ano = str(rec.get("anoCompra", ""))
                    sequencial = str(rec.get("sequencialCompra", ""))
                    if cnpj_orgao and ano and sequencial:
                        items = _fetch_contract_items(client, cnpj_orgao, ano, sequencial)
                        rec["_items"] = items
                    if (i + 1) % 50 == 0:
                        logger.info("  Fetched items for %d/%d contracts", i + 1, len(all_records))
                    time.sleep(REQUEST_DELAY)

        self._raw_contracts = all_records
        self.rows_in = len(all_records)
        logger.info("Extracted %d contracts from PNCP", self.rows_in)

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self) -> None:
        """Build Contract node dicts and VENCEU relationships."""
        contracts: list[dict] = []
        venceu_rels: list[dict] = []
        seen_ids: set[str] = set()

        for rec in self._raw_contracts:
            contract_id = self._extract_contract_id(rec)
            if not contract_id or contract_id in seen_ids:
                continue
            seen_ids.add(contract_id)

            # Monetary value — prefer homologated, fall back to estimated
            valor = (
                rec.get("valorTotalHomologado")
                or rec.get("valorTotalEstimado")
                or 0.0
            )
            try:
                valor = float(valor)
            except (TypeError, ValueError):
                valor = 0.0

            orgao = rec.get("orgaoEntidade", {})
            cnpj_orgao = orgao.get("cnpj", "")

            contract = {
                "contract_id": contract_id,
                "objeto": str(rec.get("objetoCompra", "")).strip(),
                "valor": valor,
                "orgao_contratante": (
                    orgao.get("razaoSocial", "")
                    or orgao.get("nomeUnidade", "")
                    or ""
                ).strip().upper(),
                "cnpj_orgao": cnpj_orgao,
                "data_publicacao": str(rec.get("dataPublicacaoPncp", "")).strip(),
                "data_abertura": str(rec.get("dataAberturaProposta", "")).strip(),
                "municipio": "UBERLANDIA",
                "uf": "MG",
                "modalidade": str(rec.get("modalidadeNome", rec.get("modalidadeId", ""))).strip(),
                "situacao": str(rec.get("situacaoCompraId", "")).strip(),
                "ano_compra": str(rec.get("anoCompra", "")).strip(),
                "numero_compra": str(rec.get("numeroCompra", "")).strip(),
                "numero_controle_pncp": str(rec.get("numeroControlePNCP", "")).strip(),
                "fonte": "PNCP",
            }
            contracts.append(contract)

            # Extract supplier CNPJs from items (if fetched)
            fornecedores_seen: set[str] = set()
            for item in rec.get("_items", []):
                cnpj_forn = self._extract_supplier_cnpj(item)
                if cnpj_forn and cnpj_forn not in fornecedores_seen:
                    fornecedores_seen.add(cnpj_forn)
                    venceu_rels.append({
                        "source_id": cnpj_forn,
                        "target_id": contract_id,
                    })

        self._contracts = contracts
        self._venceu_rels = venceu_rels

        logger.info(
            "Transformed %d contracts, %d VENCEU relationships",
            len(contracts),
            len(venceu_rels),
        )

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load Contract nodes and VENCEU relationships into Neo4j."""
        loaded = 0

        if self._contracts:
            logger.info("Loading %d Contract nodes ...", len(self._contracts))
            loaded += self.loader.load_nodes(
                "Contract", self._contracts, "contract_id"
            )

        if self._venceu_rels:
            logger.info("Loading %d VENCEU relationships ...", len(self._venceu_rels))
            loaded += self.loader.load_relationships(
                rel_type="VENCEU",
                rows=self._venceu_rels,
                source_label="Company",
                source_key="cnpj",
                target_label="Contract",
                target_key="contract_id",
            )

        self.rows_loaded = loaded

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_contract_id(rec: dict) -> str | None:
        """Derive a unique contract identifier from the API record."""
        # Prefer numeroControlePNCP which is globally unique
        ctrl = rec.get("numeroControlePNCP")
        if ctrl:
            return str(ctrl).strip()

        # Fallback: compose from orgao CNPJ + ano + sequencial
        orgao = rec.get("orgaoEntidade", {})
        cnpj = orgao.get("cnpj", "")
        ano = rec.get("anoCompra", "")
        seq = rec.get("sequencialCompra", "")
        if cnpj and ano and seq:
            return f"{cnpj}-{ano}-{seq}"

        return None

    @staticmethod
    def _extract_supplier_cnpj(item: dict) -> str | None:
        """Extract supplier CNPJ from a contract item dict."""
        # The items endpoint may nest supplier info in different ways
        for key in (
            "niFornecedor",
            "cnpjFornecedor",
            "fornecedor",
        ):
            val = item.get(key)
            if isinstance(val, str) and len(val) >= 11:
                return val.replace(".", "").replace("/", "").replace("-", "").strip()
            if isinstance(val, dict):
                ni = val.get("ni") or val.get("cnpj") or val.get("cpfCnpj")
                if ni and len(str(ni)) >= 11:
                    return str(ni).replace(".", "").replace("/", "").replace("-", "").strip()
        return None
