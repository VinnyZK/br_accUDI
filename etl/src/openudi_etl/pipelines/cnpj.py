"""CNPJ Pipeline — loads Companies and Partners from Receita Federal.

Processes: Estabelecimentos (filter by municipality), Empresas, Socios.
Produces: Company nodes, Person nodes, SOCIO_DE relationships.
"""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from pathlib import Path

import pandas as pd

from openudi_etl.base import Pipeline

logger = logging.getLogger(__name__)

# Receita Federal municipality code for Uberlândia
# Ref: Municipios.zip from dadosabertos.rfb.gov.br/CNPJ
RF_MUNICIPIO_UBERLANDIA = "7145"

# Column layouts (0-indexed) — CNPJ open data has no header row.
ESTAB_COLS = {
    0: "cnpj_basico",
    1: "cnpj_ordem",
    2: "cnpj_dv",
    3: "matriz_filial",
    4: "nome_fantasia",
    5: "situacao_cadastral",
    6: "data_situacao",
    7: "motivo_situacao",
    8: "cidade_exterior",
    9: "pais",
    10: "data_inicio",
    11: "cnae_principal",
    12: "cnae_secundaria",
    13: "tipo_logradouro",
    14: "logradouro",
    15: "numero",
    16: "complemento",
    17: "bairro",
    18: "cep",
    19: "uf",
    20: "municipio",
    21: "ddd1",
    22: "telefone1",
    23: "ddd2",
    24: "telefone2",
    25: "ddd_fax",
    26: "fax",
    27: "email",
    28: "situacao_especial",
    29: "data_situacao_especial",
}

EMPRESA_COLS = {
    0: "cnpj_basico",
    1: "razao_social",
    2: "natureza_juridica",
    3: "qualificacao_responsavel",
    4: "capital_social",
    5: "porte",
    6: "ente_federativo",
}

SOCIO_COLS = {
    0: "cnpj_basico",
    1: "tipo_socio",
    2: "nome_socio",
    3: "cpf_cnpj_socio",
    4: "qualificacao_socio",
    5: "data_entrada",
    6: "pais",
    7: "representante_legal",
    8: "nome_representante",
    9: "qualificacao_representante",
    10: "faixa_etaria",
}

QUALIFICACAO_MAP: dict[str, str] = {}  # loaded at runtime

SITUACAO_MAP = {
    "01": "NULA",
    "02": "ATIVA",
    "03": "SUSPENSA",
    "04": "INAPTA",
    "08": "BAIXADA",
}


def _read_zips(
    data_dir: Path,
    prefix: str,
    columns: dict[int, str],
    usecols: list[int] | None = None,
    filter_fn=None,
    chunk_size: int = 50_000,
) -> pd.DataFrame:
    """Read all ZIPs matching prefix, parse CSV, optionally filter."""
    frames: list[pd.DataFrame] = []
    zip_files = sorted(data_dir.glob(f"{prefix}*.zip"))

    if not zip_files:
        raise FileNotFoundError(
            f"No {prefix}*.zip files found in {data_dir}. "
            f"Run: make download-cnpj"
        )

    col_indices = list(columns.keys())
    col_names = list(columns.values())

    if usecols:
        col_indices = usecols
        col_names = [columns[i] for i in usecols]

    for zpath in zip_files:
        logger.info("  Reading %s", zpath.name)
        try:
            with zipfile.ZipFile(zpath) as zf:
                for name in zf.namelist():
                    if not name.upper().endswith("CSV") and "." not in name:
                        # CNPJ files have no extension or .csv
                        pass
                    with zf.open(name) as f:
                        for chunk in pd.read_csv(
                            io.TextIOWrapper(f, encoding="latin-1"),
                            sep=";",
                            header=None,
                            usecols=col_indices,
                            names=col_names,
                            dtype=str,
                            chunksize=chunk_size,
                            on_bad_lines="skip",
                            quoting=csv.QUOTE_ALL,
                        ):
                            if filter_fn:
                                chunk = filter_fn(chunk)
                            if len(chunk) > 0:
                                frames.append(chunk)
        except (zipfile.BadZipFile, Exception) as e:
            logger.warning("  Skipping %s: %s", zpath.name, e)

    if not frames:
        return pd.DataFrame(columns=col_names)

    return pd.concat(frames, ignore_index=True)


def _load_qualificacoes(data_dir: Path) -> dict[str, str]:
    """Load partner qualification codes from Qualificacoes.zip."""
    zpath = data_dir / "Qualificacoes.zip"
    if not zpath.exists():
        return {}

    result = {}
    try:
        with zipfile.ZipFile(zpath) as zf:
            for name in zf.namelist():
                with zf.open(name) as f:
                    reader = csv.reader(
                        io.TextIOWrapper(f, encoding="latin-1"),
                        delimiter=";",
                    )
                    for row in reader:
                        if len(row) >= 2:
                            result[row[0].strip()] = row[1].strip()
    except Exception as e:
        logger.warning("Could not load Qualificacoes: %s", e)

    return result


class CnpjPipeline(Pipeline):
    name = "cnpj"
    source_id = "receita_federal_cnpj"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.municipio_code = RF_MUNICIPIO_UBERLANDIA
        self.cnpj_dir = Path(self.data_dir) / "cnpj"

        # Intermediate data
        self._udi_cnpjs: set[str] = set()
        self._companies: list[dict] = []
        self._persons: list[dict] = []
        self._partnerships: list[dict] = []

    def extract(self) -> None:
        """Step 1: Read Estabelecimentos, filter for Uberlândia, collect CNPJs."""
        global QUALIFICACAO_MAP
        QUALIFICACAO_MAP = _load_qualificacoes(self.cnpj_dir)

        logger.info("Filtering Estabelecimentos for municipio=%s", self.municipio_code)

        estab_df = _read_zips(
            self.cnpj_dir,
            "Estabelecimentos",
            ESTAB_COLS,
            usecols=[0, 1, 2, 3, 4, 5, 10, 11, 19, 20],
            filter_fn=lambda df: df[df["municipio"] == self.municipio_code],
        )

        self._udi_cnpjs = set(estab_df["cnpj_basico"].unique())
        self.rows_in = len(estab_df)

        logger.info(
            "Found %d establishments, %d unique base CNPJs in Uberlândia",
            len(estab_df),
            len(self._udi_cnpjs),
        )

        # Store establishment data for enrichment
        self._estab_df = estab_df

    def transform(self) -> None:
        """Step 2: Read Empresas and Socios, filter by Uberlândia CNPJs."""
        udi_cnpjs = self._udi_cnpjs
        if not udi_cnpjs:
            logger.warning("No CNPJs found for Uberlândia. Skipping transform.")
            return

        # --- Empresas ---
        logger.info("Reading Empresas for %d CNPJs...", len(udi_cnpjs))
        empresas_df = _read_zips(
            self.cnpj_dir,
            "Empresas",
            EMPRESA_COLS,
            filter_fn=lambda df: df[df["cnpj_basico"].isin(udi_cnpjs)],
        )

        # Build full CNPJ from establishment data (base + ordem + dv)
        estab_main = self._estab_df[
            self._estab_df["matriz_filial"] == "1"
        ].drop_duplicates(subset=["cnpj_basico"], keep="first")

        # Merge empresa with establishment for full CNPJ
        merged = empresas_df.merge(
            estab_main[["cnpj_basico", "cnpj_ordem", "cnpj_dv", "situacao_cadastral",
                        "cnae_principal", "nome_fantasia"]],
            on="cnpj_basico",
            how="left",
        )

        for _, row in merged.iterrows():
            base = str(row["cnpj_basico"]).zfill(8)
            ordem = str(row.get("cnpj_ordem", "0001")).zfill(4)
            dv = str(row.get("cnpj_dv", "00")).zfill(2)
            cnpj_full = f"{base}{ordem}{dv}"

            capital = 0.0
            try:
                capital = float(str(row.get("capital_social", "0")).replace(",", "."))
            except (ValueError, TypeError):
                pass

            situacao_code = str(row.get("situacao_cadastral", ""))
            situacao = SITUACAO_MAP.get(situacao_code, situacao_code)

            self._companies.append({
                "cnpj": cnpj_full,
                "razao_social": str(row.get("razao_social", "")).strip().upper(),
                "nome_fantasia": str(row.get("nome_fantasia", "")).strip().upper()
                    if pd.notna(row.get("nome_fantasia")) else None,
                "cnae_principal": str(row.get("cnae_principal", "")).strip(),
                "capital_social": capital,
                "natureza_juridica": str(row.get("natureza_juridica", "")).strip(),
                "porte": str(row.get("porte", "")).strip(),
                "situacao": situacao,
                "municipio": "UBERLANDIA",
                "uf": "MG",
            })

        logger.info("Transformed %d companies", len(self._companies))

        # --- Socios ---
        logger.info("Reading Socios for %d CNPJs...", len(udi_cnpjs))
        socios_df = _read_zips(
            self.cnpj_dir,
            "Socios",
            SOCIO_COLS,
            filter_fn=lambda df: df[df["cnpj_basico"].isin(udi_cnpjs)],
        )

        seen_persons: set[str] = set()

        for _, row in socios_df.iterrows():
            base = str(row["cnpj_basico"]).zfill(8)
            tipo_socio = str(row.get("tipo_socio", ""))
            nome = str(row.get("nome_socio", "")).strip().upper()
            cpf_cnpj = str(row.get("cpf_cnpj_socio", "")).strip()
            qualif_code = str(row.get("qualificacao_socio", "")).strip()
            qualif = QUALIFICACAO_MAP.get(qualif_code, qualif_code)
            data_entrada = str(row.get("data_entrada", "")).strip()

            # Find full CNPJ for this company
            estab_match = estab_main[estab_main["cnpj_basico"] == base]
            if estab_match.empty:
                ordem, dv = "0001", "00"
            else:
                first = estab_match.iloc[0]
                ordem = str(first["cnpj_ordem"]).zfill(4)
                dv = str(first["cnpj_dv"]).zfill(2)
            cnpj_full = f"{base}{ordem}{dv}"

            # Person node (only for PF — tipo 2)
            if tipo_socio == "2" and cpf_cnpj and cpf_cnpj not in seen_persons:
                cpf_clean = cpf_cnpj.replace(".", "").replace("-", "").replace("*", "").strip()
                if len(cpf_clean) >= 6:  # RF masks CPFs with ***
                    self._persons.append({
                        "cpf": cpf_clean,
                        "name": nome,
                        "municipio": "UBERLANDIA",
                        "uf": "MG",
                    })
                    seen_persons.add(cpf_cnpj)

            # Partnership relationship
            self._partnerships.append({
                "source_id": cpf_cnpj.replace(".", "").replace("-", "").replace("*", "").strip()
                    if tipo_socio == "2" else cpf_cnpj,
                "target_id": cnpj_full,
                "qualificacao": qualif,
                "data_entrada": data_entrada if data_entrada != "0" else None,
                "tipo_socio": "PF" if tipo_socio == "2" else "PJ",
            })

        logger.info(
            "Transformed %d persons, %d partnerships",
            len(self._persons),
            len(self._partnerships),
        )

    def load(self) -> None:
        """Step 3: Load into Neo4j."""
        loaded = 0

        if self._companies:
            logger.info("Loading %d Company nodes...", len(self._companies))
            loaded += self.loader.load_nodes("Company", self._companies, "cnpj")

        if self._persons:
            logger.info("Loading %d Person nodes...", len(self._persons))
            loaded += self.loader.load_nodes("Person", self._persons, "cpf")

        if self._partnerships:
            # Only load PF partnerships (Person -> Company)
            pf_partnerships = [p for p in self._partnerships if p["tipo_socio"] == "PF"]
            # Remove tipo_socio from row data before loading
            for p in pf_partnerships:
                p.pop("tipo_socio", None)

            logger.info("Loading %d SOCIO_DE relationships...", len(pf_partnerships))
            loaded += self.loader.load_relationships(
                rel_type="SOCIO_DE",
                rows=pf_partnerships,
                source_label="Person",
                source_key="cpf",
                target_label="Company",
                target_key="cnpj",
                properties=["qualificacao", "data_entrada"],
            )

        self.rows_loaded = loaded
