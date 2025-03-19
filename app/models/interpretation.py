from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class InterpretationLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class InterpretationArea(str, Enum):
    GENERAL = "general"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    PERSONAL_GROWTH = "personal_growth"
    SPIRITUALITY = "spirituality"
    HEALTH = "health"
    FINANCES = "finances"


class InterpretationRequest(BaseModel):
    birth_chart_data: dict
    level: InterpretationLevel = InterpretationLevel.INTERMEDIATE
    areas: Optional[List[InterpretationArea]] = [InterpretationArea.GENERAL]
    include_transits: bool = False
    language_style: str = "professional"  # professional, casual, technical


class InterpretationResponse(BaseModel):
    status: str = "success"
    data: dict 