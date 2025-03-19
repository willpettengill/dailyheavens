from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    city: str = Field(..., description="City of birth")
    state: str = Field(..., description="State of birth")
    country: str = Field(..., description="Country of birth")
    timezone: str = Field(..., description="Timezone of birth location")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of birth location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of birth location")

class BirthChartRequest(BaseModel):
    date_of_birth: datetime = Field(..., description="Date and time of birth")
    location: Location = Field(..., description="Birth location details")

class PlanetPosition(BaseModel):
    longitude: float = Field(..., description="Longitude of the planet")
    sign: str = Field(..., description="Zodiac sign")
    house: int = Field(..., description="House number")
    qualities: Dict[str, Any] = Field(default_factory=dict, description="Planet qualities")

class HousePosition(BaseModel):
    longitude: float = Field(..., description="Longitude of the house cusp")
    sign: str = Field(..., description="Zodiac sign")
    qualities: Dict[str, Any] = Field(default_factory=dict, description="House qualities")

class BirthChartResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Birth chart data")
    location: Location = Field(..., description="Birth location details") 