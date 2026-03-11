from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import uuid4

from neo4j import Driver

from openudi_etl.loader import Neo4jBatchLoader

logger = logging.getLogger(__name__)


class Pipeline(ABC):
    name: str = ""
    source_id: str = ""

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.data_dir = data_dir
        self.limit = limit
        self.chunk_size = chunk_size
        self.loader = Neo4jBatchLoader(
            driver=driver,
            batch_size=chunk_size,
            neo4j_database=neo4j_database,
        )
        self.database = neo4j_database
        self.rows_in = 0
        self.rows_loaded = 0

    @abstractmethod
    def extract(self) -> None: ...

    @abstractmethod
    def transform(self) -> None: ...

    @abstractmethod
    def load(self) -> None: ...

    def run(self) -> None:
        run_id = str(uuid4())
        started_at = datetime.now(timezone.utc).isoformat()

        self._upsert_ingestion_run(
            run_id=run_id,
            status="running",
            started_at=started_at,
        )

        try:
            logger.info("[%s] Extracting...", self.name)
            self.extract()
            logger.info("[%s] Transforming...", self.name)
            self.transform()
            logger.info("[%s] Loading...", self.name)
            self.load()

            self._upsert_ingestion_run(
                run_id=run_id,
                status="loaded",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                rows_in=self.rows_in,
                rows_loaded=self.rows_loaded,
            )
            logger.info(
                "[%s] Done: %d rows in, %d loaded",
                self.name,
                self.rows_in,
                self.rows_loaded,
            )
        except Exception as exc:
            self._upsert_ingestion_run(
                run_id=run_id,
                status="quality_fail",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                error=str(exc),
            )
            logger.exception("[%s] Failed: %s", self.name, exc)
            raise

    def _upsert_ingestion_run(
        self,
        run_id: str,
        status: str,
        started_at: str,
        finished_at: str | None = None,
        rows_in: int = 0,
        rows_loaded: int = 0,
        error: str | None = None,
    ) -> None:
        query = (
            "MERGE (r:IngestionRun {run_id: $run_id}) "
            "SET r.source_id = $source_id, "
            "    r.status = $status, "
            "    r.started_at = $started_at, "
            "    r.finished_at = $finished_at, "
            "    r.rows_in = $rows_in, "
            "    r.rows_loaded = $rows_loaded, "
            "    r.error = $error"
        )
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                run_id=run_id,
                source_id=self.source_id,
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                rows_in=rows_in,
                rows_loaded=rows_loaded,
                error=error,
            )
