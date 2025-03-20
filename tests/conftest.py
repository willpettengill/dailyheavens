import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
from datetime import datetime
from app.main import app
from app.services.birth_chart import BirthChartService
from app.services.interpretation import InterpretationService
from app.core.logging import setup_logging
from app.models.interpretation import InterpretationArea, InterpretationLevel
import logging
import tempfile

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def birth_chart_service():
    """Create a birth chart service instance."""
    return BirthChartService()

@pytest.fixture
def interpretation_service():
    """Create an interpretation service instance."""
    return InterpretationService()

@pytest.fixture
def setup_test_logging(tmp_path_factory):
    """Set up logging for tests."""
    log_dir = tmp_path_factory.mktemp("logs")
    setup_logging(log_dir=str(log_dir), test_mode=True)

@pytest.fixture
def sample_birth_data():
    """Sample birth data for testing."""
    return {
        "date_of_birth": datetime(1990, 1, 1, 0, 0),
        "latitude": 40.7128,
        "longitude": -74.0060
    }

@pytest.fixture
def sample_birth_chart():
    """Sample birth chart for testing."""
    return {
        "planets": {
            "Sun": {"sign": "Capricorn", "house": 1, "longitude": 280.5},
            "Moon": {"sign": "Cancer", "house": 7, "longitude": 100.2},
            "Mercury": {"sign": "Sagittarius", "house": 12, "longitude": 260.8},
            "Venus": {"sign": "Aquarius", "house": 2, "longitude": 310.4},
            "Mars": {"sign": "Aries", "house": 4, "longitude": 15.7}
        },
        "houses": {
            "1": {"sign": "Capricorn", "longitude": 280.0},
            "2": {"sign": "Aquarius", "longitude": 310.0},
            "3": {"sign": "Pisces", "longitude": 340.0},
            "4": {"sign": "Aries", "longitude": 10.0},
            "5": {"sign": "Taurus", "longitude": 40.0},
            "6": {"sign": "Gemini", "longitude": 70.0},
            "7": {"sign": "Cancer", "longitude": 100.0},
            "8": {"sign": "Leo", "longitude": 130.0},
            "9": {"sign": "Virgo", "longitude": 160.0},
            "10": {"sign": "Libra", "longitude": 190.0},
            "11": {"sign": "Scorpio", "longitude": 220.0},
            "12": {"sign": "Sagittarius", "longitude": 250.0}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": "opposition", "orb": 0.3},
            {"planet1": "Sun", "planet2": "Mars", "type": "trine", "orb": 1.2},
            {"planet1": "Moon", "planet2": "Venus", "type": "square", "orb": 0.8}
        ],
        "angles": {
            "ASC": {"sign": "Capricorn", "longitude": 280.0},
            "MC": {"sign": "Libra", "longitude": 190.0},
            "DSC": {"sign": "Cancer", "longitude": 100.0},
            "IC": {"sign": "Aries", "longitude": 10.0}
        }
    }

@pytest.fixture
def load_structured_data():
    """Load structured data for testing."""
    data_dir = Path("data/structured")
    
    # Load all JSON files in the structured data directory
    structured_data = {}
    for json_file in data_dir.glob("*.json"):
        with open(json_file) as f:
            structured_data[json_file.stem] = json.load(f)
    
    return structured_data

@pytest.fixture
def sample_birth_chart_response(birth_chart_service, sample_birth_data):
    """Sample birth chart response for testing."""
    return birth_chart_service.calculate_birth_chart(
        date_of_birth=sample_birth_data["date_of_birth"],
        latitude=sample_birth_data["latitude"],
        longitude=sample_birth_data["longitude"]
    )

@pytest.fixture
def sample_interpretation_request(sample_birth_chart_response):
    """Sample interpretation request for testing."""
    return {
        "birth_chart": sample_birth_chart_response,
        "area": InterpretationArea.GENERAL.value,
        "level": InterpretationLevel.BASIC.value
    }
