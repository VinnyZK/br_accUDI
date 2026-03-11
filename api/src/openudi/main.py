from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from openudi.config import settings
from openudi.db import get_driver, close_driver
from openudi.routers import search, graph, meta, patterns


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: initialize Neo4j driver
    await get_driver()
    yield
    # Shutdown: close Neo4j driver
    await close_driver()


app = FastAPI(
    title="OpenUDI API",
    description="Uberlândia public data graph analysis tool",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(search.router)
app.include_router(graph.router)
app.include_router(meta.router)
app.include_router(patterns.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
