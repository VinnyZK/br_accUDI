"""Download CNPJ open data from Receita Federal.

Usage:
    python -m openudi_etl.scripts.download_cnpj --data-dir ../data

Downloads Empresas, Estabelecimentos, Socios and reference tables.
Supports resuming interrupted downloads.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://dadosabertos.rfb.gov.br/CNPJ"

# File groups and their counts (0-indexed)
FILE_GROUPS = {
    "Empresas": 10,
    "Estabelecimentos": 10,
    "Socios": 10,
}

REFERENCE_FILES = [
    "Cnaes.zip",
    "Municipios.zip",
    "Naturezas.zip",
    "Qualificacoes.zip",
    "Paises.zip",
    "Motivos.zip",
]


def download_file(url: str, dest: Path, timeout: float = 600) -> None:
    """Download a file with resume support."""
    dest.parent.mkdir(parents=True, exist_ok=True)

    headers: dict[str, str] = {}
    mode = "wb"
    existing_size = 0

    if dest.exists():
        existing_size = dest.stat().st_size
        headers["Range"] = f"bytes={existing_size}-"
        mode = "ab"

    with httpx.stream(
        "GET",
        url,
        headers=headers,
        timeout=timeout,
        follow_redirects=True,
    ) as response:
        if response.status_code == 416:
            logger.info("  Already complete: %s", dest.name)
            return

        if response.status_code == 206:
            logger.info("  Resuming %s from %d bytes", dest.name, existing_size)
        elif response.status_code == 200:
            mode = "wb"  # server doesn't support range, restart
        else:
            response.raise_for_status()

        total = response.headers.get("content-length")
        total_str = f" / {int(total) // (1024*1024)}MB" if total else ""

        with open(dest, mode) as f:
            downloaded = 0
            for chunk in response.iter_bytes(chunk_size=1024 * 256):
                f.write(chunk)
                downloaded += len(chunk)
                if downloaded % (1024 * 1024 * 50) < 1024 * 256:
                    logger.info(
                        "  %s: %dMB downloaded%s",
                        dest.name,
                        downloaded // (1024 * 1024),
                        total_str,
                    )

    logger.info("  Done: %s", dest.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CNPJ data")
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Directory to store downloaded files",
    )
    parser.add_argument(
        "--only",
        choices=["empresas", "estabelecimentos", "socios", "reference"],
        help="Download only a specific group",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    data_dir = Path(args.data_dir) / "cnpj"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Download reference files
    if args.only is None or args.only == "reference":
        logger.info("Downloading reference tables...")
        for filename in REFERENCE_FILES:
            url = f"{BASE_URL}/{filename}"
            dest = data_dir / filename
            try:
                download_file(url, dest)
            except Exception as e:
                logger.warning("Failed to download %s: %s", filename, e)

    # Download data groups
    for group, count in FILE_GROUPS.items():
        if args.only and args.only != group.lower():
            continue

        logger.info("Downloading %s (0-%d)...", group, count - 1)
        for i in range(count):
            filename = f"{group}{i}.zip"
            url = f"{BASE_URL}/{filename}"
            dest = data_dir / filename
            try:
                download_file(url, dest)
            except Exception as e:
                logger.warning("Failed to download %s: %s", filename, e)

    logger.info("All downloads complete. Files at: %s", data_dir)


if __name__ == "__main__":
    main()
