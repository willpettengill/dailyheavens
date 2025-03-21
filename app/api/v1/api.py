from fastapi import APIRouter

# Only import the birthchart module to avoid loading interpretation service
from app.api.v1.endpoints import birthchart, interpretation

api_router = APIRouter()
api_router.include_router(birthchart.router, tags=["birthchart"])
api_router.include_router(interpretation.router, tags=["interpretation"]) 