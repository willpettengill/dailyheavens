from fastapi import APIRouter

# Import birth chart endpoint module
from app.api.v1.endpoints import birthchart

api_router = APIRouter()
api_router.include_router(birthchart.router, tags=["birthchart"]) 