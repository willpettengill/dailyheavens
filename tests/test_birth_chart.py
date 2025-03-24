"""
Birth chart service tests for DailyHeavens

These tests verify the birth chart calculation functionality.
"""
import pytest
import random
from datetime import datetime, timedelta
import json
from pathlib import Path


def test_reference_chart(client, reference_chart_data, expected_reference_chart, save_reference_chart):
    """
    Test birth chart calculation against a known reference chart
    June 20, 1988, 4:15 AM in Newton, MA
    """
    # Send request to birth chart endpoint
    response = client.post("/api/v1/birthchart", json=reference_chart_data)
    assert response.status_code == 200, f"Birth chart API failed: {response.text}"
    
    # Check response structure
    data = response.json()
    assert "status" in data, "Response missing 'status' field"
    assert data["status"] == "success", f"Birth chart calculation failed: {data.get('error')}"
    assert "data" in data, "Response missing 'data' field"
    
    # Save the reference chart response for other tests
    chart_data = data["data"]
    save_reference_chart(chart_data)
    
    # Verify planet signs match expected values
    for planet, expected_sign in expected_reference_chart.items():
        if planet in chart_data["planets"]:
            actual_sign = chart_data["planets"][planet]["sign"]
            assert actual_sign == expected_sign, f"{planet} sign mismatch: expected {expected_sign}, got {actual_sign}"
        else:
            # Only warn for outer planets which might not be included
            if planet not in ["Neptune", "Pluto", "Uranus"]:
                pytest.fail(f"Required planet {planet} missing from chart")


def test_direct_birth_chart_calculation(birth_chart_service, reference_chart_data, expected_reference_chart):
    """Test birth chart calculation directly using the service"""
    # Parse the date and coordinates
    date_str = reference_chart_data["date_of_birth"]
    date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    latitude = reference_chart_data["latitude"]
    longitude = reference_chart_data["longitude"]
    
    # Calculate birth chart
    chart = birth_chart_service.calculate_birth_chart(
        date_of_birth=date_obj,
        latitude=latitude,
        longitude=longitude
    )
    
    # Verify planet signs match expected values
    for planet, expected_sign in expected_reference_chart.items():
        if planet in chart["planets"]:
            actual_sign = chart["planets"][planet]["sign"]
            assert actual_sign == expected_sign, f"{planet} sign mismatch: expected {expected_sign}, got {actual_sign}"
        else:
            # Only warn for outer planets which might not be included
            if planet not in ["Neptune", "Pluto", "Uranus"]:
                pytest.fail(f"Required planet {planet} missing from chart")


def test_random_chart_variety(client):
    """
    Generate multiple random birth charts to ensure variety in results
    This helps catch issues where the same chart might be returned regardless of input
    """
    # Generate 5 random birth charts with different dates and locations
    results = []
    
    for _ in range(5):
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
        test_data = {
            "date_of_birth": date_str,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Send request to birth chart endpoint
        response = client.post("/api/v1/birthchart", json=test_data)
        assert response.status_code == 200, f"Birth chart API failed for random data: {response.text}"
        
        # Extract planet signs and save to results
        data = response.json()
        planets = {p: data["data"]["planets"][p]["sign"] for p in data["data"]["planets"]}
        results.append({
            "input": test_data,
            "planets": planets
        })
    
    # Verify results are different from each other
    # Check there's at least some variety in the signs
    unique_sign_sets = set()
    for result in results:
        # Convert dict to frozenset of tuples for hashing
        sign_set = frozenset((p, s) for p, s in result["planets"].items())
        unique_sign_sets.add(sign_set)
    
    # Should have at least 2 different sign configurations out of 5 random charts
    assert len(unique_sign_sets) >= 2, "All random charts produced identical results"


def test_input_validation(client):
    """Test that invalid inputs are properly handled by the birth chart service"""
    invalid_inputs = [
        # Invalid date format
        {"date_of_birth": "20-06-1988", "latitude": 42.337, "longitude": -71.2092},
        # Out of range latitude
        {"date_of_birth": "1988-06-20T04:15:00", "latitude": 95, "longitude": -71.2092},
        # Out of range longitude
        {"date_of_birth": "1988-06-20T04:15:00", "latitude": 42.337, "longitude": -185},
        # Missing required fields
        {"date_of_birth": "1988-06-20T04:15:00", "latitude": 42.337},
        # Empty request
        {}
    ]
    
    for invalid_input in invalid_inputs:
        response = client.post("/api/v1/birthchart", json=invalid_input)
        assert response.status_code in [400, 422], f"Failed to reject invalid input: {invalid_input}"
        
        # Verify error information is provided
        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "error", f"Expected error status for invalid input, got: {data['status']}"
        assert "error" in data, "Response missing 'error' field for invalid input"


def test_edge_case_dates(client):
    """Test birth chart calculation with edge case dates"""
    edge_cases = [
        # Leap year
        {"date_of_birth": "2000-02-29T12:00:00", "latitude": 0, "longitude": 0},
        # Day before DST change
        {"date_of_birth": "2000-04-01T23:00:00", "latitude": 40, "longitude": -74},
        # Day of DST change
        {"date_of_birth": "2000-04-02T01:00:00", "latitude": 40, "longitude": -74},
        # Year change
        {"date_of_birth": "1999-12-31T23:59:59", "latitude": 0, "longitude": 0},
        # Far past
        {"date_of_birth": "1850-01-01T12:00:00", "latitude": 0, "longitude": 0}
    ]
    
    for case in edge_cases:
        response = client.post("/api/v1/birthchart", json=case)
        assert response.status_code == 200, f"Birth chart API failed for edge case: {case}"
        
        # Verify basic structure of the response
        data = response.json()
        assert "data" in data, "Response missing 'data' field"
        assert "planets" in data["data"], "Response missing 'planets' data"
        assert "houses" in data["data"], "Response missing 'houses' data" 