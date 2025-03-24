"""
End-to-end integration tests for DailyHeavens

These tests verify the full flow from birth chart calculation to interpretation.
"""
import pytest
import random
import time
from datetime import datetime
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService
from app.models.interpretation import InterpretationArea, InterpretationLevel

client = TestClient(app)

def test_birth_chart_to_interpretation_flow(client):
    """Test the complete flow from birth chart calculation to interpretation"""
    # Use the reference birth chart data
    birth_data = {
        "date_of_birth": "1988-06-20T04:15:00",
        "latitude": 42.337,
        "longitude": -71.2092
    }
    
    # Get birth chart
    chart_response = client.post("/api/v1/birthchart", json=birth_data)
    assert chart_response.status_code == 200, f"Birth chart API failed: {chart_response.text}"
    
    chart_data = chart_response.json()
    assert chart_data["status"] == "success", f"Birth chart calculation failed: {chart_data.get('error')}"
    assert "data" in chart_data, "Birth chart response missing 'data' field"
    
    birth_chart = chart_data["data"]
    
    # Send to interpretation service
    interpretation_data = {
        "birth_chart": birth_chart,
        "level": "detailed",
        "area": "general"
    }
    
    interp_response = client.post("/api/v1/interpretation", json=interpretation_data)
    assert interp_response.status_code == 200, f"Interpretation API failed: {interp_response.text}"
    
    interp_data = interp_response.json()
    assert interp_data["status"] == "success", f"Interpretation failed: {interp_data.get('error')}"
    assert "data" in interp_data, "Interpretation response missing 'data' field"
    assert "interpretations" in interp_data["data"], "Missing interpretations data"


def test_random_birth_chart_stability(client):
    """
    Test multiple random birth charts to ensure stability of the system
    Runs a sequence of chart calculations and interpretations to verify system reliability
    """
    # Run 5 sequential tests with random data
    for i in range(5):
        # Generate random but valid date (1950-2000)
        year = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Avoid month edge cases
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        
        # Random location (valid latitude/longitude)
        latitude = random.uniform(25, 65)  # Northern hemisphere, populated areas
        longitude = random.uniform(-130, 30)  # Americas and Europe
        
        # Format the data for the API request
        date_str = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
        birth_data = {
            "date_of_birth": date_str,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Calculate birth chart
        chart_response = client.post("/api/v1/birthchart", json=birth_data)
        assert chart_response.status_code == 200, f"Birth chart API failed for random data: {chart_response.text}"
        
        chart_data = chart_response.json()
        assert chart_data["status"] == "success", f"Birth chart calculation failed: {chart_data.get('error')}"
        
        birth_chart = chart_data["data"]
        
        # Get interpretation
        interpretation_data = {
            "birth_chart": birth_chart,
            "level": "detailed",
            "area": "general"
        }
        
        interp_response = client.post("/api/v1/interpretation", json=interpretation_data)
        assert interp_response.status_code == 200, f"Interpretation API failed for random data: {interp_response.text}"
        
        interp_data = interp_response.json()
        assert interp_data["status"] == "success", f"Interpretation failed: {interp_data.get('error')}"


def test_calculation_consistency(client):
    """
    Test that repeated calculations of the same birth chart are consistent
    This ensures deterministic behavior of the calculation engine
    """
    # Fixed test data
    birth_data = {
        "date_of_birth": "1975-05-15T12:30:00",
        "latitude": 34.0522,
        "longitude": -118.2437
    }
    
    # Calculate twice
    response1 = client.post("/api/v1/birthchart", json=birth_data)
    assert response1.status_code == 200, "First birth chart calculation failed"
    chart1 = response1.json()["data"]
    
    # Short delay to ensure different system time
    time.sleep(1)
    
    response2 = client.post("/api/v1/birthchart", json=birth_data)
    assert response2.status_code == 200, "Second birth chart calculation failed"
    chart2 = response2.json()["data"]
    
    # Compare planets
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if planet in chart1["planets"] and planet in chart2["planets"]:
            assert chart1["planets"][planet]["sign"] == chart2["planets"][planet]["sign"], \
                f"{planet} sign is inconsistent between calculations"
            assert chart1["planets"][planet]["house"] == chart2["planets"][planet]["house"], \
                f"{planet} house is inconsistent between calculations"
    
    # Compare house signs
    for house_num in [str(i) for i in range(1, 13)]:
        if house_num in chart1["houses"] and house_num in chart2["houses"]:
            assert chart1["houses"][house_num]["sign"] == chart2["houses"][house_num]["sign"], \
                f"House {house_num} sign is inconsistent between calculations"


def test_performance(client):
    """
    Test performance of the birth chart and interpretation services
    Measures response times for typical requests
    """
    # Test data
    birth_data = {
        "date_of_birth": "1990-01-01T12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    # Measure birth chart calculation time
    start_time = time.time()
    chart_response = client.post("/api/v1/birthchart", json=birth_data)
    chart_time = time.time() - start_time
    
    assert chart_response.status_code == 200, "Birth chart calculation failed"
    birth_chart = chart_response.json()["data"]
    
    # Measure interpretation time
    interpretation_data = {
        "birth_chart": birth_chart,
        "level": "detailed",
        "area": "general"
    }
    
    start_time = time.time()
    interp_response = client.post("/api/v1/interpretation", json=interpretation_data)
    interp_time = time.time() - start_time
    
    assert interp_response.status_code == 200, "Interpretation failed"
    
    # Log performance metrics
    print(f"\nPerformance metrics:")
    print(f"Birth chart calculation: {chart_time:.2f} seconds")
    print(f"Interpretation generation: {interp_time:.2f} seconds")
    print(f"Total time: {chart_time + interp_time:.2f} seconds")
    
    # Optional performance threshold assertions - comment out if intermittently failing in CI
    # assert chart_time < 5.0, f"Birth chart calculation too slow: {chart_time:.2f} seconds"
    # assert interp_time < 2.0, f"Interpretation generation too slow: {interp_time:.2f} seconds"


def test_health_check_during_load(client):
    """Test health endpoint remains responsive during load"""
    # Create a bunch of requests in succession to simulate load
    for _ in range(3):  # Reduced from higher number for test suite speed
        # Random but valid birth data
        year = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        birth_data = {
            "date_of_birth": f"{year}-{month:02d}-{day:02d}T12:00:00",
            "latitude": random.uniform(-80, 80),
            "longitude": random.uniform(-179, 179)
        }
        
        # Non-blocking request to create load
        client.post("/api/v1/birthchart", json=birth_data)
    
    # Health check should still be responsive
    response = client.get("/health")
    assert response.status_code == 200, "Health endpoint not responsive during load"
    
    data = response.json()
    assert "status" in data, "Health response missing 'status' field"
    assert data["status"] == "ok", f"Health status not 'ok' during load, got '{data['status']}'"

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
