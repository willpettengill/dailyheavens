import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService
from app.models.interpretation import InterpretationArea, InterpretationLevel

client = TestClient(app)

def test_birth_chart_to_interpretation_flow(client):
    """Test the flow from birth chart calculation to interpretation."""
    sample_birth_data = {
        "date_of_birth": "2000-01-01T12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    birth_chart_response = client.post("/birth-chart", json=sample_birth_data)
    assert birth_chart_response.status_code == 200
    birth_chart = birth_chart_response.json()
    
    interpretation_data = {
        **sample_birth_data,
        "level": "basic"
    }
    interpretation_response = client.post("/interpretation", json=interpretation_data)
    assert interpretation_response.status_code == 200
    interpretation = interpretation_response.json()
    
    assert "status" in interpretation
    assert interpretation["status"] == "success"
    assert "data" in interpretation

def test_interpretation_service_integration(interpretation_service):
    """Test the integration of interpretation service with birth chart data."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Aries", "house": 1},
            "Moon": {"sign": "Taurus", "house": 2},
            "Mercury": {"sign": "Gemini", "house": 3}
        },
        "houses": {
            "1": {"sign": "Aries"},
            "2": {"sign": "Taurus"},
            "3": {"sign": "Gemini"}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": "conjunction"}
        ]
    }
    
    interpretation = interpretation_service.generate_interpretation(birth_chart, level="basic")
    assert interpretation["status"] == "success"
    assert "data" in interpretation

def test_structured_data_integration(interpretation_service, load_structured_data):
    # Load all structured data
    data = load_structured_data
    
    # Verify data relationships
    planets_data = data["planets"]
    signs_data = data["signs"]
    houses_data = data["houses"]
    aspects_data = data["aspects"]
    
    # Test planet-sign relationships
    for planet, planet_data in planets_data.items():
        assert "ruling_planet" in planet_data
        ruling_planet = planet_data["ruling_planet"]
        assert ruling_planet in planets_data
    
    # Test house-sign relationships
    for house_num, house_data in houses_data.items():
        if "natural_sign" in house_data:
            sign = house_data["natural_sign"]
            assert sign in signs_data
            assert "ruling_planet" in signs_data[sign]
    
    # Test aspect relationships
    for aspect, aspect_data in aspects_data.items():
        assert "orb" in aspect_data
        assert "nature" in aspect_data
        assert "interpretation" in aspect_data

def test_error_handling_integration(client):
    # Test invalid birth data
    invalid_birth_data = {
        "date": "invalid_date",
        "latitude": "invalid_lat",
        "longitude": "invalid_lon",
        "timezone": "invalid_tz"
    }
    
    response = client.post("/api/v1/birthchart", json=invalid_birth_data)
    assert response.status_code == 422
    
    # Test invalid interpretation request
    invalid_interpretation_request = {
        "birth_chart": {},
        "area": "invalid_area",
        "level": "invalid_level"
    }
    
    response = client.post("/api/v1/interpretation", json=invalid_interpretation_request)
    assert response.status_code == 422

def test_performance_integration(client):
    """Test the performance of the integration flow."""
    sample_birth_data = {
        "date_of_birth": "2000-01-01T12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    response = client.post("/birth-chart", json=sample_birth_data)
    assert response.status_code == 200
    birth_chart = response.json()
    
    interpretation_data = {
        **sample_birth_data,
        "level": "basic"
    }
    response = client.post("/interpretation", json=interpretation_data)
    assert response.status_code == 200
    interpretation = response.json()
    
    assert "status" in interpretation
    assert interpretation["status"] == "success"
    assert "data" in interpretation

def test_data_consistency_integration(interpretation_service, load_structured_data):
    # Load all structured data
    data = load_structured_data
    
    # Test consistency between different data files
    planets_data = data["planets"]
    signs_data = data["signs"]
    dignities_data = data["planetary_dignities"]
    
    # Test planet dignities consistency
    for planet, planet_data in planets_data.items():
        assert planet in dignities_data
        planet_dignities = dignities_data[planet]
        assert "rulership" in planet_dignities
        assert "exaltation" in planet_dignities
        assert "fall" in planet_dignities
        assert "detriment" in planet_dignities
    
    # Test sign rulers consistency
    for sign, sign_data in signs_data.items():
        assert "ruling_planet" in sign_data
        ruling_planet = sign_data["ruling_planet"]
        assert ruling_planet in planets_data
        assert ruling_planet in dignities_data
