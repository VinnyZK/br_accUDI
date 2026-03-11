"""CEIS/CNEP Pipeline — loads sanctions from Portal da Transparência.

Fetches data from CEIS (Cadastro Nacional de Empresas Inidôneas e Suspensas) and
CNEP (Cadastro Nacional de Empresas Punidas) APIs, filtering for Uberlândia/MG.
Produces: Sanction nodes, SANCIONADA relationships (Company -> Sanction).
"""

from __future__ import annotations

import logging
import os
from hashlib import sha256

import httpx

from openudi_etl.base import Pipeline

logger = logging.getLogger(__name__)

CEIS_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/ceis"
CNEP_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/cnep"

IBGE_UBERLANDIA = "3170206"
UF_MG = "MG"

PAGE_SIZE = 200  # Portal da Transparência max per page
REQUEST_TIMEOUT = 60.0


def _make_sanction_id(source: str, record: dict) -> str:
    """Deterministic ID from source + key fields to allow idempotent MERGE."""
    raw = (
        f"{source}"
        f"|{record.get('cpfCnpjSancionado', '')}"
        f"|{record.get('dataInicioSancao', '')}"
        f"|{record.get('orgaoSancionador', {}).get('nome', '')}"
        f"|{record.get('fundamentacao', {}).get('descricaoFundamentacao', '')}"
    )
    return sha256(raw.encode()).hexdigest()[:24]


def _extract_cnpj(record: dict) -> str | None:
    """Return cleaned 14-digit CNPJ or None."""
    raw = record.get("cpfCnpjSancionado", "") or ""
    digits = raw.replace(".", "").replace("/", "").replace("-", "").strip()
    if len(digits) == 14:
        return digits
    return None


class CeisPipeline(Pipeline):
    name = "ceis_cnep"
    source_id = "portal_transparencia_ceis_cnep"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._api_key = os.environ.get("TRANSPARENCIA_API_KEY", "")
        if not self._api_key:
            raise EnvironmentError(
                "TRANSPARENCIA_API_KEY environment variable is required. "
                "Request one at https://portaldatransparencia.gov.br/api-de-dados"
            )

        self._raw_ceis: list[dict] = []
        self._raw_cnep: list[dict] = []

        # Transformed data
        self._sanctions: list[dict] = []
        self._relationships: list[dict] = []

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    def extract(self) -> None:
        """Fetch CEIS and CNEP records for Uberlândia/MG."""
        self._raw_ceis = self._fetch_all(CEIS_URL, "CEIS")
        self._raw_cnep = self._fetch_all(CNEP_URL, "CNEP")
        self.rows_in = len(self._raw_ceis) + len(self._raw_cnep)
        logger.info(
            "Extracted %d CEIS + %d CNEP = %d records",
            len(self._raw_ceis),
            len(self._raw_cnep),
            self.rows_in,
        )

    def _fetch_all(self, base_url: str, label: str) -> list[dict]:
        """Paginate through the API, trying municipality filter first, then UF."""
        records: list[dict] = []
        seen_keys: set[str] = set()

        # Strategy 1: filter by codigoMunicipio (most precise)
        muni_records = self._paginate(
            base_url,
            params={"codigoMunicipio": IBGE_UBERLANDIA},
            label=f"{label}/municipio",
        )
        for r in muni_records:
            key = _make_sanction_id(label, r)
            if key not in seen_keys:
                seen_keys.add(key)
                records.append(r)

        # Strategy 2: filter by ufSancionado=MG to catch broader records
        uf_records = self._paginate(
            base_url,
            params={"ufSancionado": UF_MG},
            label=f"{label}/uf",
        )
        for r in uf_records:
            key = _make_sanction_id(label, r)
            if key not in seen_keys:
                seen_keys.add(key)
                records.append(r)

        logger.info("  %s total unique: %d", label, len(records))
        return records

    def _paginate(
        self,
        base_url: str,
        params: dict,
        label: str,
    ) -> list[dict]:
        """Walk paginated API until an empty page is returned."""
        headers = {"chave-api-dados": self._api_key, "Accept": "application/json"}
        all_records: list[dict] = []
        page = 1

        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            while True:
                query = {**params, "pagina": page}
                logger.debug("  %s page %d", label, page)

                resp = client.get(base_url, headers=headers, params=query)
                resp.raise_for_status()

                data = resp.json()
                if not data:
                    break

                all_records.extend(data)

                if self.limit and len(all_records) >= self.limit:
                    all_records = all_records[: self.limit]
                    break

                page += 1

        logger.info("  %s: fetched %d records (%d pages)", label, len(all_records), page)
        return all_records

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self) -> None:
        """Build Sanction nodes and SANCIONADA relationships."""
        self._process_records(self._raw_ceis, "CEIS")
        self._process_records(self._raw_cnep, "CNEP")

        logger.info(
            "Transformed %d sanctions, %d relationships",
            len(self._sanctions),
            len(self._relationships),
        )

    def _process_records(self, records: list[dict], source: str) -> None:
        for record in records:
            cnpj = _extract_cnpj(record)
            if not cnpj:
                # Skip non-CNPJ entries (PFs without company link)
                continue

            sanction_id = _make_sanction_id(source, record)

            orgao = record.get("orgaoSancionador") or {}
            fundamento = record.get("fundamentacao") or {}

            sanction = {
                "sanction_id": sanction_id,
                "type": source,
                "company_cnpj": cnpj,
                "razao_social": (record.get("nomeSancionado") or "").strip().upper(),
                "reason": (fundamento.get("descricaoFundamentacao") or "").strip(),
                "date_start": (record.get("dataInicioSancao") or "").strip() or None,
                "date_end": (record.get("dataFimSancao") or "").strip() or None,
                "source": source,
                "orgao_sancionador": (orgao.get("nome") or "").strip(),
                "uf_sancionado": (record.get("ufSancionado") or "").strip(),
            }
            self._sanctions.append(sanction)

            self._relationships.append({
                "source_id": cnpj,
                "target_id": sanction_id,
            })

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load Sanction nodes and SANCIONADA relationships into Neo4j."""
        loaded = 0

        if self._sanctions:
            logger.info("Loading %d Sanction nodes...", len(self._sanctions))
            loaded += self.loader.load_nodes(
                "Sanction", self._sanctions, "sanction_id"
            )

        if self._relationships:
            logger.info(
                "Loading %d SANCIONADA relationships...", len(self._relationships)
            )
            loaded += self.loader.load_relationships(
                rel_type="SANCIONADA",
                rows=self._relationships,
                source_label="Company",
                source_key="cnpj",
                target_label="Sanction",
                target_key="sanction_id",
            )

        self.rows_loaded = loaded
