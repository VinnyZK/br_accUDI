from fastapi import APIRouter
from pydantic import BaseModel

from openudi.db import get_driver
from openudi.config import settings

router = APIRouter(prefix="/api/v1", tags=["meta"])


class LabelCount(BaseModel):
    label: str
    count: int


class MetaResponse(BaseModel):
    node_labels: list[LabelCount]
    total_nodes: int
    total_relationships: int


@router.get("/meta", response_model=MetaResponse)
async def get_meta() -> MetaResponse:
    """Return aggregated graph statistics for the landing page."""
    driver = await get_driver()

    node_query = """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """

    rel_query = """
        MATCH ()-[r]->()
        RETURN count(r) AS total
    """

    async with driver.session(database=settings.neo4j_database) as session:
        node_result = await session.run(node_query)
        node_records = await node_result.data()

        rel_result = await session.run(rel_query)
        rel_record = await rel_result.single()

    node_labels = [
        LabelCount(label=r["label"], count=r["count"])
        for r in node_records
    ]
    total_nodes = sum(lc.count for lc in node_labels)
    total_relationships = rel_record["total"] if rel_record else 0

    return MetaResponse(
        node_labels=node_labels,
        total_nodes=total_nodes,
        total_relationships=total_relationships,
    )
