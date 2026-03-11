"""ETL Pipeline Runner.

Usage:
    python -m openudi_etl.runner cnpj --data-dir ../data
    python -m openudi_etl.runner all --data-dir ../data
"""

from __future__ import annotations

import argparse
import logging
import sys

from neo4j import GraphDatabase

from openudi_etl.pipelines.cnpj import CnpjPipeline
from openudi_etl.pipelines.ceis import CeisPipeline
from openudi_etl.pipelines.tse import TsePipeline
from openudi_etl.pipelines.pncp import PncpPipeline

PIPELINES = {
    "cnpj": CnpjPipeline,
    "ceis": CeisPipeline,
    "tse": TsePipeline,
    "pncp": PncpPipeline,
}

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenUDI ETL Runner")
    parser.add_argument(
        "pipeline",
        choices=[*PIPELINES.keys(), "all"],
        help="Pipeline to run",
    )
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default="openudi-dev-2026")
    parser.add_argument("--neo4j-database", default="neo4j")
    parser.add_argument("--data-dir", default="./data")
    parser.add_argument("--chunk-size", type=int, default=50_000)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit rows for testing",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    driver = GraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
    )

    pipelines_to_run = (
        list(PIPELINES.keys()) if args.pipeline == "all" else [args.pipeline]
    )

    try:
        for name in pipelines_to_run:
            pipeline_cls = PIPELINES[name]
            logger.info("=" * 60)
            logger.info("Running pipeline: %s", name)
            logger.info("=" * 60)

            pipeline = pipeline_cls(
                driver=driver,
                data_dir=args.data_dir,
                limit=args.limit,
                chunk_size=args.chunk_size,
                neo4j_database=args.neo4j_database,
            )
            pipeline.run()

        logger.info("All pipelines completed successfully.")
    except Exception:
        logger.exception("Pipeline failed")
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
