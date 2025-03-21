from fastapi import APIRouter

# Only import the birthchart module for now
from app.api.v1.endpoints import birthchart

api_router = APIRouter()
api_router.include_router(birthchart.router, tags=["birthchart"])
# Temporarily comment out the interpretation router until we have time to fully fix it
# from app.api.v1.endpoints import interpretation
# api_router.include_router(interpretation.router, tags=["interpretation"]) 