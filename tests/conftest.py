"""
Test fixtures for DailyHeavens
"""
import json
import os
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi.testclient import TestClient
from app.main import app
from app.services.birth_chart import BirthChartService
from app.services.interpretation import InterpretationService
from app.core.logging import setup_logging
from app.models.interpretation import InterpretationArea, InterpretationLevel
import logging
import tempfile

@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)

@pytest.fixture
def birth_chart_service():
    """Create a birth chart service instance for isolated testing"""
    return BirthChartService()

@pytest.fixture
def interpretation_service():
    """Create an interpretation service instance for isolated testing"""
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

@pytest.fixture
def reference_chart_data():
    """
    Return reference chart data for June 20, 1988, 4:15 AM in Newton, MA
    This chart has been verified as correct and is used for regression testing
    """
    return {
        "date_of_birth": "1988-06-20T04:15:00",
        "latitude": 42.337,
        "longitude": -71.2092
    }

@pytest.fixture
def expected_reference_chart():
    """
    Expected planets and positions for the reference chart
    """
    return {
        "Sun": "Gemini",
        "Moon": "Virgo",
        "Ascendant": "Pisces",
        "Mercury": "Gemini",
        "Venus": "Gemini",
        "Mars": "Pisces",
        "Jupiter": "Taurus",
        "Saturn": "Sagittarius",
        "Neptune": "Capricorn",
        "Pluto": "Scorpio"
    }

@pytest.fixture
def saved_reference_chart_response():
    """
    Load a saved reference chart response from file to allow isolated testing
    of the interpretation service without requiring birth chart calculation
    """
    # Check if the reference file exists, if not create an empty dict
    reference_file = Path(__file__).parent / "data" / "reference_chart.json"
    if reference_file.exists():
        with open(reference_file, "r") as f:
            return json.load(f)
    else:
        # Return a minimal chart structure if file doesn't exist
        return {"planets": {}, "houses": {}, "aspects": []}

@pytest.fixture
def save_reference_chart(request):
    """
    Save a birth chart response to the reference file
    This allows capturing a real API response for future tests
    """
    def _save_chart(chart_data):
        os.makedirs(Path(__file__).parent / "data", exist_ok=True)
        reference_file = Path(__file__).parent / "data" / "reference_chart.json"
        with open(reference_file, "w") as f:
            json.dump(chart_data, f, indent=2)
        
    return _save_chart

@pytest.fixture
def sample_valid_chart_data():
    """Generate random but valid birth chart data"""
    return {
        "planets": {
            "Sun": {"sign": "Aries", "degree": 15.5, "house": 10, "retrograde": False},
            "Moon": {"sign": "Cancer", "degree": 120.8, "house": 1, "retrograde": False},
            "Mercury": {"sign": "Pisces", "degree": 340.2, "house": 9, "retrograde": True},
            "Venus": {"sign": "Taurus", "degree": 45.7, "house": 11, "retrograde": False},
            "Mars": {"sign": "Gemini", "degree": 75.3, "house": 12, "retrograde": False},
            "Jupiter": {"sign": "Libra", "degree": 195.6, "house": 5, "retrograde": False},
            "Saturn": {"sign": "Capricorn", "degree": 285.9, "house": 7, "retrograde": True},
            "Ascendant": {"sign": "Cancer", "degree": 100.0, "house": 1, "retrograde": False},
            "Midheaven": {"sign": "Aries", "degree": 10.0, "house": 10, "retrograde": False}
        },
        "houses": {
            "1": {"sign": "Cancer", "degree": 100.0, "size": 30.0},
            "2": {"sign": "Leo", "degree": 130.0, "size": 30.0},
            "3": {"sign": "Virgo", "degree": 160.0, "size": 30.0},
            "4": {"sign": "Libra", "degree": 190.0, "size": 30.0},
            "5": {"sign": "Scorpio", "degree": 220.0, "size": 30.0},
            "6": {"sign": "Sagittarius", "degree": 250.0, "size": 30.0},
            "7": {"sign": "Capricorn", "degree": 280.0, "size": 30.0},
            "8": {"sign": "Aquarius", "degree": 310.0, "size": 30.0},
            "9": {"sign": "Pisces", "degree": 340.0, "size": 30.0},
            "10": {"sign": "Aries", "degree": 10.0, "size": 30.0},
            "11": {"sign": "Taurus", "degree": 40.0, "size": 30.0},
            "12": {"sign": "Gemini", "degree": 70.0, "size": 30.0}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": 90, "orb": 5.3},
            {"planet1": "Sun", "planet2": "Venus", "type": 30, "orb": 0.8},
            {"planet1": "Moon", "planet2": "Saturn", "type": 180, "orb": 5.1},
            {"planet1": "Mercury", "planet2": "Jupiter", "type": 120, "orb": 4.6}
        ]
    }

@pytest.fixture
def sample_interpretation_request(sample_valid_chart_data):
    """Sample interpretation request using the sample chart data"""
    return {
        "birth_chart": sample_valid_chart_data,
        "level": "detailed",
        "area": "general"
    }
