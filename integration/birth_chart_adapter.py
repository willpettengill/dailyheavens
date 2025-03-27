import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import re

# Initialize FastAPI app
app = FastAPI(
    title="Daily Heavens Frontend API",
    description="API adapter for frontend integration",
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

# Create API router
api_router = APIRouter(prefix="/api")

# Configuration
BIRTH_CHART_API_URL = os.environ.get("BIRTH_CHART_API_URL", "http://localhost:8001/api/v1/birthchart")
INTERPRETATION_API_URL = os.environ.get("INTERPRETATION_API_URL", "http://localhost:8002/api/v1/interpretation")

# Hardcoded ZIP code to coordinates mapping for now
# In production, this would be replaced with a proper geocoding service
ZIP_CODE_MAP = {
    "10001": {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},  # NYC
    "90210": {"latitude": 34.0901, "longitude": -118.4065, "timezone": "America/Los_Angeles"},  # Beverly Hills
    "60601": {"latitude": 41.8781, "longitude": -87.6298, "timezone": "America/Chicago"},  # Chicago
    "33101": {"latitude": 25.7617, "longitude": -80.1918, "timezone": "America/New_York"},  # Miami
    "94102": {"latitude": 37.7749, "longitude": -122.4194, "timezone": "America/Los_Angeles"},  # San Francisco
    "02108": {"latitude": 42.3601, "longitude": -71.0589, "timezone": "America/New_York"},  # Boston
    "98101": {"latitude": 47.6062, "longitude": -122.3321, "timezone": "America/Los_Angeles"},  # Seattle
    "80202": {"latitude": 39.7392, "longitude": -104.9903, "timezone": "America/Denver"},  # Denver
    "75201": {"latitude": 32.7767, "longitude": -96.7970, "timezone": "America/Chicago"},  # Dallas
    "19102": {"latitude": 39.9526, "longitude": -75.1652, "timezone": "America/New_York"},  # Philadelphia
}

# Default coordinates for unknown ZIP codes
DEFAULT_COORDINATES = {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"}  # NYC

# Request model for frontend
class FrontendBirthChartRequest(BaseModel):
    birth_date: str = Field(..., description="Birth date in MM/DD/YYYY format")
    birth_time: str = Field(..., description="Birth time in HH:MM format (24-hour)")
    birth_place_zip: str = Field(..., description="5-digit US ZIP code")
    timezone: Optional[int] = Field(None, description="Timezone offset in hours")

# Parse date and time from frontend format
def parse_datetime(date_str: str, time_str: str, tz_offset: Optional[int] = None) -> datetime:
    """Parse date and time strings into a datetime object."""
    # Parse date (MM/DD/YYYY)
    date_match = re.match(r"(\d{2})/(\d{2})/(\d{4})", date_str)
    if not date_match:
        raise ValueError(f"Invalid date format: {date_str}. Expected MM/DD/YYYY")
    
    month, day, year = map(int, date_match.groups())
    
    # Parse time (HH:MM)
    time_match = re.match(r"(\d{2}):(\d{2})", time_str)
    if not time_match:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM (24-hour)")
    
    hour, minute = map(int, time_match.groups())
    
    # Create datetime object
    dt = datetime(year, month, day, hour, minute)
    
    return dt

# Adapt planet data to frontend format
def adapt_planet_data(planet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert our backend planet data to the frontend format."""
    return {
        "sign": planet_data.get("sign", "Unknown"),
        "degrees": float(planet_data.get("degree", 0)),
        "latitude": float(planet_data.get("latitude", 0)),
        "sign_longitude": float(planet_data.get("sign_longitude", 0)),
        "speed": float(planet_data.get("speed", 0)),
        "orb": 5.0,  # Default value
        "mean_motion": float(planet_data.get("mean_motion", 0)),
        "movement": "Retrograde" if planet_data.get("is_retrograde", False) else "Direct",
        "gender": "Masculine" if planet_data.get("gender", "") == "masculine" else 
                 "Feminine" if planet_data.get("gender", "") == "feminine" else "Unknown",
        "element": planet_data.get("element", "Unknown").capitalize(),
        "is_fast": planet_data.get("is_fast", True),
        "house": int(planet_data.get("house", 1))
    }

# Adapt house data to frontend format
def adapt_house_data(house_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert our backend house data to the frontend format."""
    return {
        "sign": house_data.get("sign", "Unknown"),
        "degrees": float(house_data.get("degree", 0)),
        "sign_longitude": float(house_data.get("sign_longitude", 0)),
        "condition": house_data.get("condition", "Unknown"),
        "gender": "Masculine" if house_data.get("gender", "") == "masculine" else "Feminine",
        "size": float(house_data.get("size", 30.0)),
        "planets": house_data.get("planets", [])
    }

# Adapt angle data to frontend format
def adapt_angle_data(angle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert our backend angle data to the frontend format."""
    return {
        "sign": angle_data.get("sign", "Unknown"),
        "degrees": float(angle_data.get("degree", 0)),
        "sign_longitude": float(angle_data.get("sign_longitude", 0))
    }

# Get coordinates from ZIP code
def get_coordinates_from_zip(zip_code: str) -> Dict[str, Any]:
    """Get coordinates from a ZIP code."""
    if zip_code in ZIP_CODE_MAP:
        return ZIP_CODE_MAP[zip_code]
    return DEFAULT_COORDINATES

# Main birth chart endpoint
@api_router.post("/birth-chart")
async def calculate_birth_chart(request: FrontendBirthChartRequest = Body(...)):
    """Calculate a birth chart based on frontend request format."""
    try:
        # Get coordinates from ZIP code
        coordinates = get_coordinates_from_zip(request.birth_place_zip)
        
        # Parse date and time
        birth_datetime = parse_datetime(request.birth_date, request.birth_time)
        
        # Format datetime for our backend API
        formatted_datetime = birth_datetime.isoformat()
        
        # Prepare request for our backend API
        backend_request = {
            "date": formatted_datetime,
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "timezone": coordinates["timezone"]
        }
        
        # Call our birth chart API
        async with httpx.AsyncClient() as client:
            response = await client.post(BIRTH_CHART_API_URL, json=backend_request, timeout=30.0)
            
            if response.status_code != 200:
                return {
                    "error": f"Birth chart API error: {response.status_code}",
                    "message": response.text
                }
            
            birth_chart_data = response.json()
            
            if birth_chart_data.get("status") != "success":
                return {
                    "error": "Birth chart calculation failed",
                    "message": birth_chart_data.get("error", "Unknown error")
                }
            
            # Extract the actual data
            backend_data = birth_chart_data.get("data", {})
            
            # Transform to frontend format
            planets_data = {k.lower(): v for k, v in backend_data.get("planets", {}).items()}
            houses_data = backend_data.get("houses", {})
            angles_data = backend_data.get("angles", {})
            
            # Define expected planets and houses
            expected_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
            expected_houses = [f"house{i}" for i in range(1, 13)]
            expected_angles = ["ascendant", "midheaven", "descendant", "imum_coeli"]
            
            # Transform planet data
            frontend_planets = {}
            for planet in expected_planets:
                if planet in planets_data:
                    frontend_planets[planet] = adapt_planet_data(planets_data[planet])
                else:
                    # Use placeholder data for missing planets
                    frontend_planets[planet] = {
                        "sign": "Unknown",
                        "degrees": 0.0,
                        "latitude": 0.0,
                        "sign_longitude": 0.0,
                        "speed": 0.0,
                        "orb": 5.0,
                        "mean_motion": 0.0,
                        "movement": "Direct",
                        "gender": "Unknown",
                        "element": "Unknown",
                        "is_fast": False,
                        "house": 1
                    }
            
            # Transform house data
            frontend_houses = {}
            for house in expected_houses:
                house_number = house.replace("house", "")
                if house_number in houses_data:
                    frontend_houses[house] = adapt_house_data(houses_data[house_number])
                else:
                    # Use placeholder data for missing houses
                    frontend_houses[house] = {
                        "sign": "Unknown",
                        "degrees": 0.0,
                        "sign_longitude": 0.0,
                        "condition": "Unknown",
                        "gender": "Unknown",
                        "size": 30.0,
                        "planets": []
                    }
            
            # Transform angle data
            frontend_angles = {}
            for angle in expected_angles:
                if angle in angles_data:
                    frontend_angles[angle] = adapt_angle_data(angles_data[angle])
                else:
                    # Use placeholder data for missing angles
                    frontend_angles[angle] = {
                        "sign": "Unknown",
                        "degrees": 0.0,
                        "sign_longitude": 0.0
                    }
            
            # Prepare aspects data
            aspects = []
            for aspect_data in backend_data.get("aspects", []):
                aspect_type = aspect_data.get("type", "")
                # Convert numeric aspect types to string names
                aspect_names = {
                    0: "conjunction",
                    60: "sextile",
                    90: "square",
                    120: "trine",
                    180: "opposition",
                    150: "quincunx"
                }
                
                if isinstance(aspect_type, (int, float)):
                    aspect_type = aspect_names.get(int(aspect_type), str(aspect_type))
                
                if aspect_type:
                    aspects.append({
                        "planet1": aspect_data.get("planet1", ""),
                        "planet2": aspect_data.get("planet2", ""),
                        "aspect": aspect_type,
                        "orb": float(aspect_data.get("orb", 0)),
                        "nature": aspect_data.get("nature", "neutral")
                    })
            
            # Final frontend response format
            frontend_response = {
                "planets": frontend_planets,
                "houses": frontend_houses,
                "angles": frontend_angles,
                "aspects": aspects
            }
            
            return frontend_response
            
    except ValueError as e:
        return {
            "error": "Invalid input",
            "message": str(e)
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Daily Heavens Frontend API",
        "version": "1.0.0",
        "status": "operational"
    }

# Include API router
app.include_router(api_router)

# If run directly, start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 