import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService
from app.models.interpretation import InterpretationArea, InterpretationLevel

client = TestClient(app)

@pytest.fixture
def sample_birth_data():
    return {
        "date": "1990-01-01T12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York"
    }

def test_birth_chart_calculation_performance(client, sample_birth_data):
    # Test single request
    start_time = time.time()
    response = client.post("/api/v1/birthchart", json=sample_birth_data)
    single_request_time = time.time() - start_time
    
    assert response.status_code == 200
    assert single_request_time < 2.0  # Should complete within 2 seconds
    
    # Test multiple concurrent requests
    import concurrent.futures
    num_requests = 10
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(client.post, "/api/v1/birthchart", json=sample_birth_data)
            for _ in range(num_requests)
        ]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    avg_time = total_time / num_requests
    
    assert all(r.status_code == 200 for r in responses)
    assert avg_time < 2.0  # Average time should be under 2 seconds

def test_interpretation_generation_performance(client, sample_birth_data):
    # Get birth chart data first
    birth_chart_response = client.post("/api/v1/birthchart", json=sample_birth_data)
    birth_chart_data = birth_chart_response.json()["data"]
    
    # Test single interpretation request
    interpretation_request = {
        "birth_chart": birth_chart_data,
        "area": InterpretationArea.GENERAL.value,
        "level": InterpretationLevel.BASIC.value
    }
    
    start_time = time.time()
    response = client.post("/api/v1/interpretation", json=interpretation_request)
    single_request_time = time.time() - start_time
    
    assert response.status_code == 200
    assert single_request_time < 3.0  # Should complete within 3 seconds
    
    # Test multiple concurrent interpretation requests
    import concurrent.futures
    num_requests = 10
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(client.post, "/api/v1/interpretation", json=interpretation_request)
            for _ in range(num_requests)
        ]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    avg_time = total_time / num_requests
    
    assert all(r.status_code == 200 for r in responses)
    assert avg_time < 3.0  # Average time should be under 3 seconds

def test_structured_data_loading_performance(interpretation_service):
    # Test initial data loading
    start_time = time.time()
    interpretation_service._load_structured_data()
    load_time = time.time() - start_time
    
    assert load_time < 1.0  # Should load within 1 second
    
    # Test repeated data loading (should be cached)
    start_time = time.time()
    interpretation_service._load_structured_data()
    reload_time = time.time() - start_time
    
    assert reload_time < 0.1  # Should be much faster due to caching

def test_memory_usage_performance(interpretation_service, sample_birth_data):
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Generate multiple interpretations
    birth_chart_response = client.post("/api/v1/birthchart", json=sample_birth_data)
    birth_chart_data = birth_chart_response.json()["data"]
    
    interpretation_request = {
        "birth_chart": birth_chart_data,
        "area": InterpretationArea.GENERAL.value,
        "level": InterpretationLevel.BASIC.value
    }
    
    for _ in range(100):
        client.post("/api/v1/interpretation", json=interpretation_request)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 100MB)
    assert memory_increase < 100 * 1024 * 1024

def test_response_size_performance(client, sample_birth_data):
    # Test birth chart response size
    birth_chart_response = client.post("/api/v1/birthchart", json=sample_birth_data)
    birth_chart_size = len(birth_chart_response.content)
    
    assert birth_chart_size < 100 * 1024  # Less than 100KB
    
    # Test interpretation response size
    birth_chart_data = birth_chart_response.json()["data"]
    interpretation_request = {
        "birth_chart": birth_chart_data,
        "area": InterpretationArea.GENERAL.value,
        "level": InterpretationLevel.BASIC.value
    }
    
    interpretation_response = client.post("/api/v1/interpretation", json=interpretation_request)
    interpretation_size = len(interpretation_response.content)
    
    assert interpretation_size < 500 * 1024  # Less than 500KB

def test_error_handling_performance(client):
    # Test invalid request handling time
    invalid_data = {
        "date": "invalid_date",
        "latitude": "invalid_lat",
        "longitude": "invalid_lon",
        "timezone": "invalid_tz"
    }
    
    start_time = time.time()
    response = client.post("/api/v1/birthchart", json=invalid_data)
    error_handling_time = time.time() - start_time
    
    assert response.status_code == 422
    assert error_handling_time < 0.5  # Should handle errors quickly
