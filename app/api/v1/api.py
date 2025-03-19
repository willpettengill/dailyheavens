from fastapi import APIRouter

from app.api.v1.endpoints import birthchart, interpretation

api_router = APIRouter()
api_router.include_router(birthchart.router, tags=["birthchart"])
api_router.include_router(interpretation.router, tags=["interpretation"]) 