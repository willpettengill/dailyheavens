import os
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from index import app  # Import the FastAPI app

# Create test client
client = TestClient(app)

# Mock data
MOCK_BIRTH_CHART_RESPONSE = {
    "status": "success",
    "planets": [
        {"name": "Sun", "sign": "Gemini", "degree": 25.5, "house": 10, "retrograde": False},
        {"name": "Moon", "sign": "Virgo", "degree": 15.2, "house": 1, "retrograde": False},
        {"name": "Mercury", "sign": "Gemini", "degree": 20.1, "house": 10, "retrograde": False},
        {"name": "Venus", "sign": "Cancer", "degree": 5.3, "house": 11, "retrograde": False},
        {"name": "Mars", "sign": "Aries", "degree": 10.7, "house": 8, "retrograde": False},
        {"name": "Jupiter", "sign": "Aquarius", "degree": 12.3, "house": 6, "retrograde": True},
        {"name": "Saturn", "sign": "Capricorn", "degree": 8.9, "house": 5, "retrograde": True}
    ],
    "houses": [
        {"house": 1, "sign": "Virgo", "degree": 15.0},
        {"house": 2, "sign": "Libra", "degree": 15.0},
        {"house": 3, "sign": "Scorpio", "degree": 15.0},
        {"house": 4, "sign": "Sagittarius", "degree": 15.0},
        {"house": 5, "sign": "Capricorn", "degree": 15.0},
        {"house": 6, "sign": "Aquarius", "degree": 15.0},
        {"house": 7, "sign": "Pisces", "degree": 15.0},
        {"house": 8, "sign": "Aries", "degree": 15.0},
        {"house": 9, "sign": "Taurus", "degree": 15.0},
        {"house": 10, "sign": "Gemini", "degree": 15.0},
        {"house": 11, "sign": "Cancer", "degree": 15.0},
        {"house": 12, "sign": "Leo", "degree": 15.0}
    ],
    "aspects": [
        {"planet1": "Sun", "planet2": "Moon", "aspect": "trine", "orb": 2.3},
        {"planet1": "Mercury", "planet2": "Saturn", "aspect": "square", "orb": 1.5}
    ],
    "calculation_date": datetime.now().isoformat(),
    "location": {"latitude": 40.7128, "longitude": -74.0060}
}

MOCK_INTERPRETATION_RESPONSE = {
    "status": "success",
    "planet_interpretations": [
        {
            "planet": "Sun",
            "sign": "Gemini",
            "house": 10,
            "interpretation": "Your Sun in Gemini gives you an adaptable and curious nature. You're mentally agile and communicate easily."
        },
        {
            "planet": "Moon",
            "sign": "Virgo",
            "house": 1,
            "interpretation": "Your Moon in Virgo suggests you find emotional security through organization and practical matters."
        }
    ],
    "house_interpretations": [
        {
            "house": 1,
            "sign": "Virgo",
            "interpretation": "With Virgo on your first house cusp, you present yourself to the world as analytical and detail-oriented."
        },
        {
            "house": 10,
            "sign": "Gemini",
            "interpretation": "With Gemini on your tenth house cusp, your career may involve communication, versatility, and intellectual pursuits."
        }
    ],
    "aspect_interpretations": []
}

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

@patch("httpx.AsyncClient.post")
def test_birth_chart_success(mock_post):
    """Test successful birth chart and interpretation."""
    # Configure mock responses
    mock_birth_chart = MagicMock()
    mock_birth_chart.status_code = 200
    mock_birth_chart.json.return_value = MOCK_BIRTH_CHART_RESPONSE
    
    mock_interpretation = MagicMock()
    mock_interpretation.status_code = 200
    mock_interpretation.json.return_value = MOCK_INTERPRETATION_RESPONSE
    
    # Set up the mock to return our test responses
    mock_post.side_effect = [mock_birth_chart, mock_interpretation]
    
    # Test request
    request_data = {
        "birth_date": "06/15/1988",
        "birth_time": "14:30",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    response = client.post("/birth-chart", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "birth_chart" in data
    assert "interpretation" in data
    assert data["birth_chart"]["status"] == "success"
    assert data["interpretation"]["status"] == "success"

@patch("httpx.AsyncClient.post")
def test_birth_chart_with_zip_code(mock_post):
    """Test birth chart with ZIP code."""
    # Configure mock responses
    mock_birth_chart = MagicMock()
    mock_birth_chart.status_code = 200
    mock_birth_chart.json.return_value = MOCK_BIRTH_CHART_RESPONSE
    
    mock_interpretation = MagicMock()
    mock_interpretation.status_code = 200
    mock_interpretation.json.return_value = MOCK_INTERPRETATION_RESPONSE
    
    # Set up the mock to return our test responses
    mock_post.side_effect = [mock_birth_chart, mock_interpretation]
    
    # Test request with ZIP code
    request_data = {
        "birth_date": "06/15/1988",
        "birth_time": "14:30",
        "zip_code": "10001"
    }
    
    response = client.post("/birth-chart", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "birth_chart" in data
    assert "interpretation" in data

@patch("httpx.AsyncClient.post")
def test_birth_chart_partial_success(mock_post):
    """Test when birth chart succeeds but interpretation fails."""
    # Configure mock responses
    mock_birth_chart = MagicMock()
    mock_birth_chart.status_code = 200
    mock_birth_chart.json.return_value = MOCK_BIRTH_CHART_RESPONSE
    
    mock_interpretation = MagicMock()
    mock_interpretation.status_code = 500
    mock_interpretation.text = "Internal server error"
    
    # Set up the mock to return our test responses
    mock_post.side_effect = [mock_birth_chart, mock_interpretation]
    
    # Test request
    request_data = {
        "birth_date": "06/15/1988",
        "birth_time": "14:30",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    response = client.post("/birth-chart", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "partial_success"
    assert "birth_chart" in data
    assert "interpretation_error" in data

def test_invalid_request_format():
    """Test with invalid request format."""
    # Test request with invalid date format
    request_data = {
        "birth_date": "15-06-1988",  # Wrong format
        "birth_time": "14:30"
    }
    
    response = client.post("/birth-chart", json=request_data)
    assert response.status_code == 400

@patch("httpx.AsyncClient.post")
def test_birth_chart_service_error(mock_post):
    """Test when birth chart service returns error."""
    # Configure mock response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    # Set up the mock to return our error response
    mock_post.return_value = mock_response
    
    # Test request
    request_data = {
        "birth_date": "06/15/1988",
        "birth_time": "14:30",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    response = client.post("/birth-chart", json=request_data)
    assert response.status_code == 500
    data = response.json()
    
    assert data["status"] == "error"
    assert "message" in data 