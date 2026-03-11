"""TSE Pipeline — loads candidates, donations, and declared assets.

Source: https://dadosabertos.tse.jus.br/dataset/
Files are CSV, downloaded per election year.
Produces: Person nodes (is_pep=true), PublicOffice nodes, CANDIDATO relationships,
          Company->PublicOffice DOOU_PARA relationships.
"""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from pathlib import Path

import httpx
import pandas as pd

from openudi_etl.base import Pipeline

logger = logging.getLogger(__name__)

# TSE open data base URL
TSE_BASE = "https://dadosabertos.tse.jus.br/dataset"

# Download URLs for election data (2020 municipal + 2024 municipal)
# Files are ZIP archives from TSE CDN
TSE_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand"
TSE_FILES = {
    "consulta_cand_2024": f"{TSE_CDN}/consulta_cand_2024.zip",
    "consulta_cand_2020": f"{TSE_CDN}/consulta_cand_2020.zip",
}

# Uberlândia municipality code in TSE data
TSE_MUNICIPIO_UBERLANDIA = "61492"  # TSE electoral zone code
UDI_MUNICIPIO_NAME = "UBERLÂNDIA"

# State code for MG
TSE_UF_MG = "MG"


def _download_tse_file(url: str, dest: Path, timeout: float = 600) -> None:
    """Download a TSE file."""
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("  Already downloaded: %s", dest.name)
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("  Downloading %s...", dest.name)

    with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_bytes(chunk_size=256 * 1024):
                f.write(chunk)

    logger.info("  Done: %s (%d KB)", dest.name, dest.stat().st_size // 1024)


def _read_tse_csv(
    filepath: Path,
    usecols: list[str] | None = None,
    filter_fn=None,
) -> pd.DataFrame:
    """Read a TSE CSV file (latin-1, semicolon-delimited, with header)."""
    frames: list[pd.DataFrame] = []

    # TSE files can be CSV or inside ZIP
    if filepath.suffix == ".zip":
        with zipfile.ZipFile(filepath) as zf:
            for name in zf.namelist():
                if name.endswith(".csv"):
                    with zf.open(name) as f:
                        for chunk in pd.read_csv(
                            io.TextIOWrapper(f, encoding="latin-1"),
                            sep=";",
                            usecols=usecols,
                            dtype=str,
                            chunksize=50_000,
                            on_bad_lines="skip",
                            quoting=csv.QUOTE_ALL,
                        ):
                            if filter_fn:
                                chunk = filter_fn(chunk)
                            if len(chunk) > 0:
                                frames.append(chunk)
    else:
        for chunk in pd.read_csv(
            filepath,
            sep=";",
            encoding="latin-1",
            usecols=usecols,
            dtype=str,
            chunksize=50_000,
            on_bad_lines="skip",
            quoting=csv.QUOTE_ALL,
        ):
            if filter_fn:
                chunk = filter_fn(chunk)
            if len(chunk) > 0:
                frames.append(chunk)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


class TsePipeline(Pipeline):
    name = "tse"
    source_id = "tse_eleicoes"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tse_dir = Path(self.data_dir) / "tse"

        self._persons: list[dict] = []
        self._offices: list[dict] = []
        self._candidacies: list[dict] = []

    def extract(self) -> None:
        """Download TSE candidate files."""
        self.tse_dir.mkdir(parents=True, exist_ok=True)

        # Try to find local files first (user may have downloaded manually)
        local_files = list(self.tse_dir.glob("consulta_cand_*.csv")) + \
                      list(self.tse_dir.glob("consulta_cand_*.zip"))

        if local_files:
            logger.info("Found %d local TSE files", len(local_files))
            self._candidate_files = local_files
            return

        # Download from TSE CDN (ZIP files)
        self._candidate_files = []
        for key, url in TSE_FILES.items():
            dest = self.tse_dir / f"{key}.zip"
            try:
                _download_tse_file(url, dest)
                self._candidate_files.append(dest)
            except Exception as e:
                logger.warning("Failed to download %s: %s", key, e)

        if not self._candidate_files:
            raise FileNotFoundError(
                "No TSE candidate files found. "
                "Download manually to data/tse/ or check connectivity."
            )

    def transform(self) -> None:
        """Parse candidate data, filter for Uberlândia."""
        candidate_cols = [
            "SG_UF", "NM_UE", "NM_CANDIDATO", "NR_CPF_CANDIDATO",
            "DS_CARGO", "NR_ANO_ELEICAO", "DS_SIT_TOT_TURNO",
            "NM_MUNICIPIO_NASCIMENTO", "DS_GRAU_INSTRUCAO",
            "VR_DESPESA_MAX_CAMPANHA", "NR_PARTIDO", "SG_PARTIDO",
        ]

        all_candidates = pd.DataFrame()

        for filepath in self._candidate_files:
            logger.info("Reading %s", filepath.name)
            try:
                df = _read_tse_csv(
                    filepath,
                    usecols=lambda col: col in candidate_cols,
                    filter_fn=lambda df: df[
                        (df["SG_UF"] == TSE_UF_MG) &
                        (df["NM_UE"].str.upper().str.contains("UBERLÂNDIA|UBERLANDIA", na=False))
                    ] if "NM_UE" in df.columns and "SG_UF" in df.columns else df,
                )
                if len(df) > 0:
                    all_candidates = pd.concat([all_candidates, df], ignore_index=True)
            except Exception as e:
                logger.warning("Error reading %s: %s", filepath.name, e)

        if all_candidates.empty:
            logger.warning("No candidates found for Uberlândia")
            return

        self.rows_in = len(all_candidates)
        logger.info("Found %d candidates for Uberlândia", len(all_candidates))

        seen_cpfs: set[str] = set()
        seen_offices: set[str] = set()

        for _, row in all_candidates.iterrows():
            cpf = str(row.get("NR_CPF_CANDIDATO", "")).strip()
            nome = str(row.get("NM_CANDIDATO", "")).strip().upper()
            cargo = str(row.get("DS_CARGO", "")).strip()
            ano = str(row.get("NR_ANO_ELEICAO", "")).strip()
            situacao = str(row.get("DS_SIT_TOT_TURNO", "")).strip()
            partido = str(row.get("SG_PARTIDO", "")).strip()

            if not cpf or cpf == "nan" or len(cpf) < 6:
                continue

            cpf_clean = cpf.replace(".", "").replace("-", "").strip()

            # Person node
            if cpf_clean not in seen_cpfs:
                self._persons.append({
                    "cpf": cpf_clean,
                    "name": nome,
                    "is_pep": True,
                    "cargo": cargo,
                    "partido": partido,
                    "municipio": "UBERLANDIA",
                    "uf": "MG",
                })
                seen_cpfs.add(cpf_clean)

            # PublicOffice node
            office_id = f"ELEC-UDI-{ano}-{cpf_clean[-6:]}"
            if office_id not in seen_offices:
                self._offices.append({
                    "office_id": office_id,
                    "year": int(ano) if ano.isdigit() else 0,
                    "cargo": cargo,
                    "municipio": "UBERLANDIA",
                    "uf": "MG",
                    "situacao": situacao,
                    "partido": partido,
                })
                seen_offices.add(office_id)

                # Candidacy relationship
                self._candidacies.append({
                    "source_id": cpf_clean,
                    "target_id": office_id,
                })

        logger.info(
            "Transformed: %d persons, %d offices, %d candidacies",
            len(self._persons),
            len(self._offices),
            len(self._candidacies),
        )

    def load(self) -> None:
        """Load into Neo4j."""
        loaded = 0

        if self._persons:
            logger.info("Loading %d Person nodes (PEPs)...", len(self._persons))
            loaded += self.loader.load_nodes("Person", self._persons, "cpf")

        if self._offices:
            logger.info("Loading %d PublicOffice nodes...", len(self._offices))
            loaded += self.loader.load_nodes("PublicOffice", self._offices, "office_id")

        if self._candidacies:
            logger.info("Loading %d CANDIDATO relationships...", len(self._candidacies))
            loaded += self.loader.load_relationships(
                rel_type="CANDIDATO",
                rows=self._candidacies,
                source_label="Person",
                source_key="cpf",
                target_label="PublicOffice",
                target_key="office_id",
            )

        self.rows_loaded = loaded
