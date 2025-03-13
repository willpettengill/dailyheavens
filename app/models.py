from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr, field_validator

class BirthInfo(BaseModel):
    birth_date: str  # Format: "MM/DD/YYYY"
    birth_time: Optional[str] = "12:00"  # Format: "HH:MM", default to noon if not provided
    birth_place_zip: constr(pattern=r'^\d{5}$')  # US ZIP code
    email: Optional[str] = None
    name: Optional[str] = None
    
    @field_validator('birth_date')
    def validate_birth_date(cls, v):
        try:
            # Try to parse the date in MM/DD/YYYY format
            datetime.strptime(v, '%m/%d/%Y')
            return v
        except ValueError:
            try:
                # Try alternative format with 2-digit year
                date_obj = datetime.strptime(v, '%m/%d/%y')
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                raise ValueError('Date must be in MM/DD/YYYY format')

class ChartResponse(BaseModel):
    sun_sign: str
    moon_sign: str
    ascendant: str
    houses: dict[str, dict]
    planets: dict[str, dict]
    interpretation: str

class EmailRequest(BaseModel):
    email: str
    chart_id: str
