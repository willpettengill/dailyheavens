import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title="Daily Heavens API",
    description="Unified API for Daily Heavens astrology services",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BIRTH_CHART_API_URL = os.environ.get("BIRTH_CHART_API_URL", "http://localhost:8001/api/v1/birthchart")
INTERPRETATION_API_URL = os.environ.get("INTERPRETATION_API_URL", "http://localhost:8002/api/v1/interpretation")

# Request model for frontend
class BirthChartRequest(BaseModel):
    birth_date: str = Field(..., description="Birth date in MM/DD/YYYY format")
    birth_time: str = Field(..., description="Birth time in HH:MM format (24-hour)")
    latitude: Optional[float] = Field(None, description="Latitude of birth place")
    longitude: Optional[float] = Field(None, description="Longitude of birth place")
    location: Optional[str] = Field(None, description="Location name (city, country)")
    zip_code: Optional[str] = Field(None, description="ZIP code of birth place")

# Error handler middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An internal server error occurred", "error_type": str(type(e).__name__)},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Converts MM/DD/YYYY HH:MM to ISO format
def format_datetime(date_str: str, time_str: str) -> str:
    try:
        # Parse date and time strings
        month, day, year = map(int, date_str.split('/'))
        hour, minute = map(int, time_str.split(':'))
        
        # Create datetime object and convert to ISO format
        dt = datetime(year, month, day, hour, minute)
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error formatting datetime: {str(e)}")
        raise ValueError(f"Invalid date/time format: {date_str} {time_str}. Expected MM/DD/YYYY HH:MM")

# Hardcoded ZIP code to coordinates mapping
ZIP_CODE_MAP = {
    "10001": {"latitude": 40.7128, "longitude": -74.0060},  # NYC
    "90210": {"latitude": 34.0901, "longitude": -118.4065},  # Beverly Hills
    "60601": {"latitude": 41.8781, "longitude": -87.6298},  # Chicago
    "33101": {"latitude": 25.7617, "longitude": -80.1918},  # Miami
    "94102": {"latitude": 37.7749, "longitude": -122.4194},  # San Francisco
}

# Default coordinates
DEFAULT_COORDINATES = {"latitude": 40.7128, "longitude": -74.0060}  # NYC

@app.post("/birth-chart")
async def get_birth_chart(request: BirthChartRequest):
    """
    Get a birth chart based on birth details.
    This unified endpoint handles both birth chart calculation and interpretation.
    """
    try:
        # Resolve coordinates from zip code if provided
        latitude = request.latitude
        longitude = request.longitude
        
        if not (latitude and longitude) and request.zip_code:
            location_data = ZIP_CODE_MAP.get(request.zip_code, DEFAULT_COORDINATES)
            latitude = location_data["latitude"]
            longitude = location_data["longitude"]
            logger.info(f"Using coordinates from ZIP code {request.zip_code}: {latitude}, {longitude}")
        
        if not (latitude and longitude):
            # Use default coordinates if none provided
            latitude = DEFAULT_COORDINATES["latitude"]
            longitude = DEFAULT_COORDINATES["longitude"]
            logger.info(f"Using default coordinates: {latitude}, {longitude}")
        
        # Format date for backend service
        iso_datetime = format_datetime(request.birth_date, request.birth_time)
        
        # Prepare request for birth chart service
        birth_chart_payload = {
            "date": iso_datetime,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Call birth chart service
        logger.info(f"Requesting birth chart with payload: {birth_chart_payload}")
        async with httpx.AsyncClient() as client:
            try:
                birth_chart_response = await client.post(
                    BIRTH_CHART_API_URL,
                    json=birth_chart_payload,
                    timeout=30.0
                )
                
                if birth_chart_response.status_code != 200:
                    logger.error(f"Birth chart service error: {birth_chart_response.text}")
                    return JSONResponse(
                        status_code=birth_chart_response.status_code,
                        content={
                            "status": "error",
                            "message": f"Birth chart service error: {birth_chart_response.status_code}",
                            "details": birth_chart_response.text
                        }
                    )
                
                birth_chart_data = birth_chart_response.json()
                
                # Handle missing outer planets warning but continue processing
                planets = birth_chart_data.get("planets", [])
                for planet in ["Uranus", "Neptune", "Pluto"]:
                    if not any(p.get("name") == planet for p in planets):
                        logger.warning(f"Planet {planet} not found in chart, continuing with available planets")
                
                # Call interpretation service
                interpretation_payload = {
                    "birth_chart": birth_chart_data,
                    "level": "detailed",
                    "area": "general"
                }
                
                logger.info("Requesting interpretation")
                interpretation_response = await client.post(
                    INTERPRETATION_API_URL,
                    json=interpretation_payload,
                    timeout=30.0
                )
                
                if interpretation_response.status_code != 200:
                    logger.error(f"Interpretation service error: {interpretation_response.text}")
                    # Return birth chart anyway even if interpretation fails
                    return {
                        "status": "partial_success",
                        "message": "Birth chart calculated successfully but interpretation failed",
                        "birth_chart": birth_chart_data,
                        "interpretation_error": interpretation_response.text
                    }
                
                interpretation_data = interpretation_response.json()
                
                # Return combined response
                return {
                    "status": "success",
                    "birth_chart": birth_chart_data,
                    "interpretation": interpretation_data
                }
                
            except httpx.RequestError as e:
                logger.error(f"Request error calling backend service: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Service unavailable: {str(e)}"
                )
                
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 