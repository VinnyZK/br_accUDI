from fastapi import APIRouter, Query
from pydantic import BaseModel

from openudi.db import get_driver
from openudi.config import settings

router = APIRouter(prefix="/api/v1", tags=["search"])


def mask_cpf(cpf: str | None) -> str | None:
    """Mask CPF showing only last 2 digits: ***.***.***-XX."""
    if cpf is None:
        return None
    digits = cpf.replace(".", "").replace("-", "").strip()
    if len(digits) < 2:
        return cpf
    return f"***.***.***.{digits[-2:]}"


class SearchResult(BaseModel):
    type: str
    id: str
    display_name: str | None = None
    cpf: str | None = None
    cnpj: str | None = None
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> SearchResponse:
    """Full-text search across all entities using the Neo4j entity_search index."""
    driver = await get_driver()

    cypher = """
        CALL db.index.fulltext.queryNodes('entity_search', $term)
        YIELD node, score
        RETURN labels(node)[0] AS type,
               elementId(node) AS id,
               node.name AS name,
               coalesce(node.razao_social, node.name) AS display_name,
               node.cpf AS cpf,
               node.cnpj AS cnpj,
               score
        ORDER BY score DESC
        LIMIT $limit
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(cypher, term=q, limit=limit)
        records = await result.data()

    results = [
        SearchResult(
            type=record["type"],
            id=record["id"],
            display_name=record["display_name"],
            cpf=mask_cpf(record.get("cpf")),
            cnpj=record.get("cnpj"),
            score=record["score"],
        )
        for record in records
    ]

    return SearchResponse(results=results, total=len(results))
