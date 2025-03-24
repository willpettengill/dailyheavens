from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.interpretation import (
    InterpretationArea,
    InterpretationLevel,
    InterpretationRequest,
    InterpretationResponse
)
from app.services.interpretation import InterpretationService

router = APIRouter()
interpretation_service = InterpretationService()

@router.post("/interpretation", response_model=InterpretationResponse)
async def generate_interpretation(request: InterpretationRequest) -> InterpretationResponse:
    """Generate astrological interpretation."""
    try:
        # Validate birth chart structure
        if not request.birth_chart.get("planets"):
            raise ValueError("Birth chart must contain planetary positions")
            
        # Generate interpretation
        interpretation = interpretation_service.generate_interpretation(
            birth_chart=request.birth_chart,
            level=request.level.value,
            area=request.area.value
        )
        
        if interpretation["status"] == "error":
            return InterpretationResponse(
                status="error",
                data={},
                error=interpretation["message"]
            )
            
        return InterpretationResponse(
            status="success",
            data=interpretation["data"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating interpretation: {str(e)}"
        ) 