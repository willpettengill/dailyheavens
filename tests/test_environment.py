"""
Environment and setup tests for DailyHeavens

These tests verify that the environment is correctly set up and that
required dependencies are available and functioning properly.
"""
import pytest
import importlib
import sys
import logging
from pathlib import Path


def test_python_version():
    """Check that we're running on a compatible Python version"""
    major, minor = sys.version_info.major, sys.version_info.minor
    assert major == 3, f"Expected Python 3, got Python {major}"
    assert minor >= 9, f"Expected Python 3.9+, got Python {major}.{minor}"


def test_flatlib_availability():
    """Verify that flatlib is available and properly installed"""
    try:
        import flatlib
        assert flatlib.__name__ == "flatlib", "Failed to import flatlib"
        
        # Check specific modules needed for chart calculation
        from flatlib.datetime import Datetime
        from flatlib.geopos import GeoPos
        from flatlib.chart import Chart
        from flatlib import const
        
        # Basic test of functionality
        date = Datetime("2000/1/1", "12:00", "+00:00")
        pos = GeoPos(0.0, 0.0)
        chart = Chart(date, pos)
        
        # Access a planet to verify basic functionality
        sun = chart.getObject(const.SUN)
        assert sun is not None, "Failed to get Sun object from chart"
        assert hasattr(sun, "sign"), "Sun object missing 'sign' attribute"
        
    except ImportError as e:
        pytest.fail(f"flatlib import error: {str(e)}")
    except Exception as e:
        pytest.fail(f"flatlib usage error: {str(e)}")


def test_services_initialization():
    """Test that the core services initialize properly"""
    try:
        from app.services.birth_chart import BirthChartService
        birth_chart_service = BirthChartService()
        assert birth_chart_service is not None, "Failed to initialize BirthChartService"
        
        from app.services.interpretation import InterpretationService
        interpretation_service = InterpretationService()
        assert interpretation_service is not None, "Failed to initialize InterpretationService"
    except ImportError as e:
        pytest.fail(f"Failed to import services: {str(e)}")
    except Exception as e:
        pytest.fail(f"Failed to initialize services: {str(e)}")


def test_data_directories():
    """Test that required data directories exist"""
    # Base dir is the parent directory of the app package
    base_dir = Path(__file__).parent.parent
    
    # Check for structured data directory
    structured_data_dir = base_dir / "data" / "structured"
    assert structured_data_dir.exists(), f"Structured data directory not found: {structured_data_dir}"
    
    # Check for log directory
    log_dir = base_dir / "logs"
    if not log_dir.exists():
        logging.warning(f"Log directory not found: {log_dir}")
        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)


def test_api_health_endpoint(client):
    """Test that the API health endpoint is responsive"""
    response = client.get("/health")
    assert response.status_code == 200, "Health endpoint failed"
    
    data = response.json()
    assert "status" in data, "Health response missing 'status' field"
    assert data["status"] == "healthy", f"Health status not 'healthy', got '{data['status']}'" 