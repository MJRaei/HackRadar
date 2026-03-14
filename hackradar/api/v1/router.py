from fastapi import APIRouter

from hackradar.api.v1 import criteria, judging, projects

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(projects.router)
api_router.include_router(criteria.router)
api_router.include_router(judging.router)
