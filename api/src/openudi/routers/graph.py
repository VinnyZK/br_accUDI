from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Any

from openudi.db import get_driver
from openudi.config import settings

router = APIRouter(prefix="/api/v1", tags=["graph"])


class GraphNode(BaseModel):
    id: str
    label: str
    properties: dict[str, Any]


class GraphEdge(BaseModel):
    id: str
    type: str
    source: str
    target: str
    properties: dict[str, Any]


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def _sanitize_properties(props: dict[str, Any]) -> dict[str, Any]:
    """Remove or mask sensitive fields from node properties."""
    sanitized = dict(props)
    if "cpf" in sanitized and sanitized["cpf"] is not None:
        digits = sanitized["cpf"].replace(".", "").replace("-", "").strip()
        if len(digits) >= 2:
            sanitized["cpf"] = f"***.***.***.{digits[-2:]}"
    return sanitized


@router.get("/graph/{element_id:path}", response_model=GraphResponse)
async def get_subgraph(
    element_id: str,
    depth: int = Query(2, ge=1, le=5, description="Traversal depth"),
) -> GraphResponse:
    """Fetch a subgraph around an entity by its Neo4j element ID."""
    driver = await get_driver()

    query = """
        MATCH (center) WHERE elementId(center) = $element_id
        CALL apoc.path.subgraphAll(center, {maxLevel: $depth})
        YIELD nodes, relationships
        UNWIND nodes AS n
        WITH collect(DISTINCT {
            id: elementId(n),
            label: labels(n)[0],
            properties: properties(n)
        }) AS nodeList, relationships
        UNWIND relationships AS r
        RETURN nodeList AS nodes,
               collect(DISTINCT {
                   id: elementId(r),
                   type: type(r),
                   source: elementId(startNode(r)),
                   target: elementId(endNode(r)),
                   properties: properties(r)
               }) AS edges
    """

    async with driver.session(database=settings.neo4j_database) as session:
        result = await session.run(query, element_id=element_id, depth=depth)
        record = await result.single()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity not found: {element_id}",
        )

    nodes = [
        GraphNode(
            id=n["id"],
            label=n["label"],
            properties=_sanitize_properties(n["properties"]),
        )
        for n in record["nodes"]
    ]

    edges = [
        GraphEdge(
            id=e["id"],
            type=e["type"],
            source=e["source"],
            target=e["target"],
            properties=e["properties"],
        )
        for e in record["edges"]
    ]

    return GraphResponse(nodes=nodes, edges=edges)
