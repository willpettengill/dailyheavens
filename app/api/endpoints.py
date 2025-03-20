from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..services.birth_chart import BirthChartService
from ..services.interpretation import InterpretationService
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

router = APIRouter()
birth_chart_service = BirthChartService()
interpretation_service = InterpretationService()

class BirthChartRequest(BaseModel):
    date_of_birth: str = Field(..., description="Date of birth in ISO format (YYYY-MM-DD)")
    latitude: float = Field(..., description="Latitude of birth location", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of birth location", ge=-180, le=180)

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class InterpretationRequest(BaseModel):
    date_of_birth: str = Field(..., description="Date of birth in ISO format (YYYY-MM-DD)")
    latitude: float = Field(..., description="Latitude of birth location", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of birth location", ge=-180, le=180)
    level: str = Field("basic", description="Level of interpretation detail", pattern="^(basic|detailed)$")
    area: str = Field("general", description="Area of life to focus interpretation on", pattern="^(general|career|relationships|health|spirituality|personal_growth)$")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

@router.post("/birth-chart")
async def calculate_birth_chart(request: BirthChartRequest) -> Dict[str, Any]:
    """Calculate a birth chart based on date and location."""
    try:
        birth_chart = birth_chart_service.calculate_birth_chart(
            request.date_of_birth,
            request.latitude,
            request.longitude
        )
        
        return {
            "status": "success",
            "data": birth_chart
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error calculating birth chart: {str(e)}"
        }

@router.post("/interpretation")
async def generate_interpretation(request: InterpretationRequest) -> Dict[str, Any]:
    """Generate an interpretation based on birth chart data."""
    try:
        interpretation = interpretation_service.generate_interpretation(
            date_of_birth=request.date_of_birth,
            latitude=request.latitude,
            longitude=request.longitude,
            level=request.level,
            area=request.area
        )
        
        return interpretation
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating interpretation: {str(e)}"
        }

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 