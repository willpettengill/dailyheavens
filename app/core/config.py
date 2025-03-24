from pathlib import Path
from typing import List

class Settings:
    PROJECT_NAME: str = "DailyHeavens API"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    DATA_DIR: Path = Path(__file__).parent.parent.parent / "data"
    FLATLIB_EPHE_PATH: str = str(Path(__file__).parent.parent.parent / "ephe")

    class Config:
        case_sensitive = True

settings = Settings() 