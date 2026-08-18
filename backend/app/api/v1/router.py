from fastapi import APIRouter

from app.api.v1.routes import health, knowledge_graphs, workflows

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    knowledge_graphs.router,
    prefix="/knowledge-graphs",
    tags=["knowledge-graphs"],
)
api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["workflows"],
)
