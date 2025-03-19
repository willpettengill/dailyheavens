from fastapi import APIRouter, Depends

from app.models.interpretation import InterpretationRequest, InterpretationResponse
from app.services.interpretation import InterpretationService

router = APIRouter()


@router.post("/interpretation", response_model=InterpretationResponse)
async def generate_interpretation(
    request: InterpretationRequest,
    interpretation_service: InterpretationService = Depends(lambda: InterpretationService())
) -> InterpretationResponse:
    """
    Generate an astrological interpretation based on birth chart data.
    
    Parameters:
    - birth_chart_data: The birth chart data from the /birthchart endpoint
    - level: The depth of interpretation (basic, intermediate, advanced)
    - areas: List of life areas to focus on
    - include_transits: Whether to include current transits
    - language_style: Style of the interpretation text
    
    Returns:
    - Detailed astrological interpretation based on the provided parameters
    """
    interpretation = interpretation_service.generate_interpretation(
        birth_chart_data=request.birth_chart_data,
        level=request.level,
        areas=request.areas,
        include_transits=request.include_transits,
        language_style=request.language_style
    )
    
    return InterpretationResponse(data=interpretation) 