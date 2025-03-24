"""
Interpretation service tests for DailyHeavens

These tests verify the interpretation functionality with different charts.
"""
import pytest
import random
import json
from pathlib import Path


def test_reference_chart_interpretation(client, saved_reference_chart_response):
    """Test interpretation of the reference chart"""
    # Skip if we don't have a saved reference chart
    if not saved_reference_chart_response.get("planets"):
        pytest.skip("No reference chart available")
    
    # Create interpretation request
    interpretation_data = {
        "birth_chart": saved_reference_chart_response,
        "level": "detailed",
        "area": "general"
    }
    
    # Send request to interpretation endpoint
    response = client.post("/api/v1/interpretation", json=interpretation_data)
    assert response.status_code == 200, f"Interpretation API failed: {response.text}"
    
    # Check response structure
    data = response.json()
    assert "status" in data, "Response missing 'status' field"
    assert data["status"] == "success", f"Interpretation failed: {data.get('error')}"
    assert "data" in data, "Response missing 'data' field"
    
    # Verify interpretation components exist
    interp_data = data["data"]
    assert "interpretations" in interp_data, "Missing interpretations data"
    assert "planets" in interp_data["interpretations"], "Missing planet interpretations"
    assert "houses" in interp_data["interpretations"], "Missing house interpretations"
    assert "aspects" in interp_data["interpretations"], "Missing aspect interpretations"
    
    # Verify other components
    assert "planetary_dignities" in interp_data, "Missing planetary dignities"
    assert "element_modality_balance" in interp_data, "Missing element/modality balance"
    assert "patterns" in interp_data, "Missing patterns analysis"


def test_various_interpretation_components(interpretation_service, sample_valid_chart_data):
    """Test interpretation of various components to ensure all methods are exercised"""
    # Call service directly to interpret chart
    interpretation = interpretation_service.generate_interpretation(
        birth_chart=sample_valid_chart_data,
        level="detailed",
        area="general"
    )
    
    # Check basic interpretation components
    assert "planets" in interpretation["interpretations"], "Missing planet interpretations"
    assert "houses" in interpretation["interpretations"], "Missing house interpretations"
    assert "aspects" in interpretation["interpretations"], "Missing aspect interpretations"
    
    # Check advanced components that might be missed in normal testing
    assert "planetary_dignities" in interpretation, "Missing planetary dignities"
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        assert planet in interpretation["planetary_dignities"], f"Missing dignity for {planet}"
    
    # Check element/modality balance
    assert "element_modality_balance" in interpretation, "Missing element/modality balance"
    balance = interpretation["element_modality_balance"]
    assert "counts" in balance, "Missing element/modality counts"
    assert "percentages" in balance, "Missing element/modality percentages"
    assert "dominant" in balance, "Missing dominant element/modality"
    assert "lacking" in balance, "Missing lacking element/modality"
    
    # Check pattern recognition
    assert "patterns" in interpretation, "Missing pattern recognition"
    assert "stelliums" in interpretation["patterns"], "Missing stellium patterns"
    assert "t_squares" in interpretation["patterns"], "Missing T-square patterns"
    assert "grand_trines" in interpretation["patterns"], "Missing grand trine patterns"


def test_pattern_recognition(interpretation_service):
    """Test that the interpretation service can identify different chart patterns"""
    # Create a chart with a stellium (3+ planets in same sign)
    stellium_chart = {
        "planets": {
            "Sun": {"sign": "Aries", "degree": 15.5, "house": 1, "retrograde": False},
            "Moon": {"sign": "Aries", "degree": 10.8, "house": 1, "retrograde": False},
            "Mercury": {"sign": "Aries", "degree": 5.2, "house": 1, "retrograde": False},
            "Venus": {"sign": "Taurus", "degree": 45.7, "house": 2, "retrograde": False},
            "Mars": {"sign": "Gemini", "degree": 75.3, "house": 3, "retrograde": False},
            "Jupiter": {"sign": "Libra", "degree": 195.6, "house": 7, "retrograde": False},
            "Saturn": {"sign": "Capricorn", "degree": 285.9, "house": 10, "retrograde": True},
            "Ascendant": {"sign": "Aries", "degree": 0.0, "house": 1, "retrograde": False},
            "Midheaven": {"sign": "Capricorn", "degree": 270.0, "house": 10, "retrograde": False}
        },
        "houses": {
            "1": {"sign": "Aries", "degree": 0.0, "size": 30.0},
            "2": {"sign": "Taurus", "degree": 30.0, "size": 30.0},
            "3": {"sign": "Gemini", "degree": 60.0, "size": 30.0},
            "4": {"sign": "Cancer", "degree": 90.0, "size": 30.0},
            "5": {"sign": "Leo", "degree": 120.0, "size": 30.0},
            "6": {"sign": "Virgo", "degree": 150.0, "size": 30.0},
            "7": {"sign": "Libra", "degree": 180.0, "size": 30.0},
            "8": {"sign": "Scorpio", "degree": 210.0, "size": 30.0},
            "9": {"sign": "Sagittarius", "degree": 240.0, "size": 30.0},
            "10": {"sign": "Capricorn", "degree": 270.0, "size": 30.0},
            "11": {"sign": "Aquarius", "degree": 300.0, "size": 30.0},
            "12": {"sign": "Pisces", "degree": 330.0, "size": 30.0}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": 0, "orb": 4.7},
            {"planet1": "Sun", "planet2": "Mercury", "type": 0, "orb": 10.3},
            {"planet1": "Moon", "planet2": "Mercury", "type": 0, "orb": 5.6}
        ]
    }
    
    # Interpret the chart
    interpretation = interpretation_service.generate_interpretation(
        birth_chart=stellium_chart,
        level="detailed",
        area="general"
    )
    
    # Verify patterns identified
    assert "patterns" in interpretation, "Missing pattern recognition"
    assert "stelliums" in interpretation["patterns"], "Missing stellium patterns"
    
    # Should find a stellium in Aries with Sun, Moon, Mercury
    found_stellium = False
    for stellium in interpretation["patterns"]["stelliums"]:
        if stellium["sign"] == "Aries" and set(stellium["planets"]) == {"Sun", "Moon", "Mercury"}:
            found_stellium = True
            break
    
    assert found_stellium, "Failed to identify Aries stellium with Sun, Moon, Mercury"


def test_error_handling(client):
    """Test error handling in the interpretation service"""
    # Missing birth chart
    response = client.post("/api/v1/interpretation", json={
        "level": "detailed",
        "area": "general"
    })
    assert response.status_code in [400, 422], "Failed to reject missing birth chart"
    
    # Invalid level
    response = client.post("/api/v1/interpretation", json={
        "birth_chart": {"planets": {}, "houses": {}, "aspects": []},
        "level": "invalid_level",
        "area": "general"
    })
    assert response.status_code in [400, 422], "Failed to reject invalid interpretation level"
    
    # Invalid area
    response = client.post("/api/v1/interpretation", json={
        "birth_chart": {"planets": {}, "houses": {}, "aspects": []},
        "level": "detailed",
        "area": "invalid_area"
    })
    assert response.status_code in [400, 422], "Failed to reject invalid interpretation area"


def test_interpretation_combinations(client, saved_reference_chart_response):
    """Test different combinations of interpretation levels and areas"""
    # Skip if we don't have a saved reference chart
    if not saved_reference_chart_response.get("planets"):
        pytest.skip("No reference chart available")
    
    # Test all combinations of levels and areas
    levels = ["basic", "detailed"]
    areas = ["general", "love", "career", "personality"]
    
    for level in levels:
        for area in areas:
            # Create interpretation request
            interpretation_data = {
                "birth_chart": saved_reference_chart_response,
                "level": level,
                "area": area
            }
            
            # Send request to interpretation endpoint
            response = client.post("/api/v1/interpretation", json=interpretation_data)
            assert response.status_code == 200, f"Interpretation API failed for {level}/{area}: {response.text}"
            
            # Check response structure
            data = response.json()
            assert data["status"] == "success", f"Interpretation failed for {level}/{area}: {data.get('error')}"
            
            # Verify basic components exist
            interp_data = data["data"]
            assert "interpretations" in interp_data, f"Missing interpretations for {level}/{area}" 