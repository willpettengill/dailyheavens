from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.birth_chart import BirthChartService

router = APIRouter()
birth_chart_service = BirthChartService()

class BirthChartRequest(BaseModel):
    date: datetime
    latitude: float
    longitude: float
    timezone: str

class BirthChartResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]

@router.post("/birthchart", response_model=BirthChartResponse)
async def calculate_birth_chart(request: BirthChartRequest) -> BirthChartResponse:
    """Calculate birth chart data."""
    try:
        chart_data = birth_chart_service.calculate_birth_chart(
            date_of_birth=request.date,
            latitude=request.latitude,
            longitude=request.longitude
        )
        return BirthChartResponse(
            status="success",
            data=chart_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating birth chart: {str(e)}"
        ) 