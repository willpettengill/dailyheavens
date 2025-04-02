from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import os # Added os
from jinja2 import Environment, FileSystemLoader # Added Jinja2 imports

from app.models.interpretation import (
    InterpretationArea,
    InterpretationLevel,
    InterpretationRequest,
    InterpretationResponse
)
from app.services.interpretation import InterpretationService

router = APIRouter()

# Define a dependency function to get the service
def get_interpretation_service():
    # Create a new service instance
    service = InterpretationService()
    
    # FORCE Jinja2 environment reload for debugging
    # Adjust path to correctly point to templates directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    templates_dir = os.path.join(project_root, "templates")  # Removed the redundant "app" folder in the path
    service.jinja_env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        auto_reload=True 
    )
    service.logger.debug(f"Forcing Jinja environment reload in dependency. Templates dir: {templates_dir}")
    
    return service

@router.post("/interpretation", response_model=InterpretationResponse)
async def generate_interpretation(
    request: InterpretationRequest,
    # Inject the service instance using Depends
    interpretation_service: InterpretationService = Depends(get_interpretation_service)
) -> InterpretationResponse:
    """Generate astrological interpretation."""
    try:
        # Validate birth chart structure
        if not request.birth_chart or not request.birth_chart.get("planets"):
            raise ValueError("Birth chart data must contain planetary positions")
            
        # Generate interpretation using the injected service
        interpretation = interpretation_service.generate_interpretation(
            birth_chart=request.birth_chart,
            level=request.level.value
        )
        
        # Check for error response from the service itself
        if isinstance(interpretation, dict) and interpretation.get("status") == "error":
            # Pass the specific error message from the service if available
            error_msg = interpretation.get("message", "Interpretation service failed")
            # Log the error server-side for debugging
            # logger.error(f"Interpretation service error: {error_msg}") 
            raise ValueError(error_msg) # Raise ValueError to be caught below
            
        # Return successful response with interpretation
        return InterpretationResponse(
            status="success",
            data={"birth_chart": request.birth_chart, "interpretations": interpretation}
        )
    except ValueError as e:
        # Handle validation errors or errors explicitly raised from the service
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        # Catch unexpected errors
        # Log the full error for debugging
        # logger.exception(f"Unexpected error generating interpretation: {str(e)}") 
        raise HTTPException(
            status_code=500,
            detail=f"Error generating interpretation: {str(e)}"
        ) 