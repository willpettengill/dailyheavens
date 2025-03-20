from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pytz import timezone

from app.services.birth_chart import BirthChartService

router = APIRouter()
birth_chart_service = BirthChartService()

class BirthChartRequest(BaseModel):
    date: datetime = Field(..., description="Date and time of birth")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")
    timezone: str = Field("UTC", description="Timezone of birth location")

class BirthChartResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None

@router.post("/birthchart", response_model=BirthChartResponse)
async def calculate_birth_chart(request: BirthChartRequest) -> BirthChartResponse:
    """Calculate birth chart data."""
    try:
        # Convert to UTC for calculation
        tz = timezone(request.timezone)
        utc_date = request.date.astimezone(timezone('UTC'))
        
        chart_data = birth_chart_service.calculate_birth_chart(
            date_of_birth=utc_date.isoformat(),
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        if chart_data["status"] == "error":
            return BirthChartResponse(
                status="error",
                data={},
                error=chart_data["error"]
            )
            
        return BirthChartResponse(
            status="success",
            data=chart_data["data"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating birth chart: {str(e)}"
        ) 