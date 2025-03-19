from fastapi import APIRouter, HTTPException

from app.models.interpretation import (
    InterpretationRequest,
    InterpretationResponse,
    InterpretationArea,
    InterpretationLevel
)
from app.services.interpretation import InterpretationService

router = APIRouter()
interpretation_service = InterpretationService()

@router.post("/interpretation", response_model=InterpretationResponse)
async def generate_interpretation(request: InterpretationRequest) -> InterpretationResponse:
    """Generate astrological interpretation."""
    try:
        return interpretation_service.generate_interpretation(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating interpretation: {str(e)}"
        ) 