from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class InterpretationLevel(str, Enum):
    BASIC = "basic"
    DETAILED = "detailed"


class InterpretationArea(str, Enum):
    GENERAL = "general"
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
    area: InterpretationArea = InterpretationArea.GENERAL
    level: InterpretationLevel = InterpretationLevel.BASIC


class InterpretationResponse(BaseModel):
    status: str
    data: Dict[str, Any] = Field(
        default_factory=lambda: {
            "interpretations": {
                "planets": [],
                "houses": [],
                "aspects": [],
                "patterns": [],
                "configurations": []
            },
            "patterns": [],
            "combinations": {},
            "house_emphasis": {},
            "special_configurations": []
        }
    )
    error: Optional[str] = None 