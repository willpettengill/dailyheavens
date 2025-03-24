import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.interpretation import InterpretationArea, InterpretationLevel

client = TestClient(app)

def test_birth_chart_endpoint_response_structure(client):
    """Test the structure of the birth chart endpoint response."""
    response = client.post(
        "/birth-chart",
        json={
            "date_of_birth": "2000-01-01T12:00:00",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "planets" in data["data"]
    assert "houses" in data["data"]
    assert "aspects" in data["data"]
    assert "angles" in data["data"]

def test_interpretation_endpoint_response_structure(client):
    """Test the structure of the interpretation endpoint response."""
    response = client.post(
        "/interpretation",
        json={
            "date_of_birth": "2000-01-01T12:00:00",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "level": "basic"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "interpretations" in data["data"]
    assert "aspect_interpretations" in data["data"]
    assert "house_interpretations" in data["data"]
    assert "patterns" in data["data"]
    assert "combinations" in data["data"]
    assert "house_emphasis" in data["data"]
    assert "special_configurations" in data["data"]

def test_interpretation_area_validation(client):
    """Test validation of interpretation area."""
    response = client.post("/api/v1/interpretation", json={
        "birth_chart": {
            "planets": {},
            "houses": {},
            "aspects": [],
            "angles": {}
        },
        "area": "invalid_area",
        "level": "basic"
    })
    
    assert response.status_code == 422
    error_data = response.json()
    assert "status" in error_data
    assert error_data["status"] == "error"
    assert "error" in error_data

def test_interpretation_level_validation(client):
    """Test validation of interpretation level."""
    response = client.post("/api/v1/interpretation", json={
        "birth_chart": {
            "planets": {},
            "houses": {},
            "aspects": [],
            "angles": {}
        },
        "area": "general",
        "level": "invalid_level"
    })
    
    assert response.status_code == 422
    error_data = response.json()
    assert "status" in error_data
    assert error_data["status"] == "error"
    assert "error" in error_data

def test_error_response_structure(client):
    """Test the structure of error responses."""
    # Test with missing required fields
    response = client.post("/birth-chart", json={})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    
    # Test with invalid date format
    response = client.post("/birth-chart", json={
        "date_of_birth": "invalid-date",
        "latitude": 40.7128,
        "longitude": -74.0060
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    
    # Test with out of range coordinates
    response = client.post("/birth-chart", json={
        "date_of_birth": "1990-01-01T00:00:00Z",
        "latitude": 100,
        "longitude": 200
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_invalid_interpretation_level(client):
    """Test that an invalid interpretation level returns an error."""
    response = client.post(
        "/interpretation",
        json={
            "date_of_birth": "2000-01-01T12:00:00",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "level": "invalid"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data
