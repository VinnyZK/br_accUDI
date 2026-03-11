from __future__ import annotations

import logging
import time

from neo4j import Driver
from neo4j.exceptions import TransientError

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


class Neo4jBatchLoader:
    def __init__(
        self,
        driver: Driver,
        batch_size: int = 10_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.batch_size = batch_size
        self.database = neo4j_database

    def load_nodes(
        self,
        label: str,
        rows: list[dict],
        key_field: str,
    ) -> int:
        rows = [r for r in rows if r.get(key_field) is not None]
        if not rows:
            return 0

        props = ", ".join(
            f"n.{k} = row.{k}" for k in rows[0] if k != key_field
        )
        query = (
            f"UNWIND $rows AS row "
            f"MERGE (n:{label} {{{key_field}: row.{key_field}}}) "
            f"SET {props}"
        )

        return self._run_batched(query, rows)

    def load_relationships(
        self,
        rel_type: str,
        rows: list[dict],
        source_label: str,
        source_key: str,
        target_label: str,
        target_key: str,
        properties: list[str] | None = None,
    ) -> int:
        if not rows:
            return 0

        prop_clause = ""
        if properties:
            prop_clause = ", ".join(f"r.{p} = row.{p}" for p in properties)
            prop_clause = f" SET {prop_clause}"

        query = (
            f"UNWIND $rows AS row "
            f"MATCH (a:{source_label} {{{source_key}: row.source_id}}) "
            f"MATCH (b:{target_label} {{{target_key}: row.target_id}}) "
            f"MERGE (a)-[r:{rel_type}]->(b)"
            f"{prop_clause}"
        )

        return self._run_batched(query, rows)

    def _run_batched(self, query: str, rows: list[dict]) -> int:
        total = 0
        for i in range(0, len(rows), self.batch_size):
            batch = rows[i : i + self.batch_size]
            total += self._run_with_retry(query, batch)
        return total

    def _run_with_retry(self, query: str, rows: list[dict]) -> int:
        for attempt in range(MAX_RETRIES):
            try:
                with self.driver.session(database=self.database) as session:
                    result = session.run(query, rows=rows)
                    counters = result.consume().counters
                    return (
                        counters.nodes_created
                        + counters.relationships_created
                        + counters.properties_set
                    )
            except TransientError:
                wait = 2**attempt
                logger.warning(
                    "TransientError on attempt %d, retrying in %ds",
                    attempt + 1,
                    wait,
                )
                time.sleep(wait)
        raise RuntimeError(f"Failed after {MAX_RETRIES} retries")
