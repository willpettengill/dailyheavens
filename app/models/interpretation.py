from enum import Enum
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class InterpretationLevel(str, Enum):
    BASIC = "basic"
    DETAILED = "detailed"


class InterpretationArea(str, Enum):
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    SPIRITUALITY = "spirituality"
    PERSONAL_GROWTH = "personal_growth"


class BirthData(BaseModel):
    date: datetime
    latitude: float
    longitude: float
    timezone: str


class InterpretationRequest(BaseModel):
    birth_chart: Dict[str, Any]
    area: InterpretationArea
    level: InterpretationLevel = InterpretationLevel.BASIC


class InterpretationResponse(BaseModel):
    status: str
    data: Dict[str, Any] = Field(
        default_factory=lambda: {
            "interpretations": [],
            "patterns": {
                "elemental": None,
                "modality": None,
                "sun_moon": None,
                "sun_rising": None,
                "moon_rising": None,
                "house_emphasis": None
            },
            "techniques_used": []
        }
    ) 