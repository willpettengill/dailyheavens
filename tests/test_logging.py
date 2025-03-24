import pytest
import logging
import json
from pathlib import Path
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService
from app.models.interpretation import InterpretationArea, InterpretationLevel
from app.core.logging import setup_logging, get_logger

@pytest.fixture
def sample_birth_data():
    return {
        "date": "1990-01-01T12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York"
    }

def test_logging_configuration(tmp_path):
    """Test that logging is properly configured."""
    log_file = tmp_path / "test.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app")
    assert len(logger.handlers) > 0
    logger.info("Test log message")
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Test log message" in log_content

def test_birth_chart_logging(tmp_path):
    """Test logging during birth chart calculation."""
    log_file = tmp_path / "birth_chart.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app.services.birth_chart")
    
    # Log a sample birth chart calculation
    logger.info("Calculating birth chart")
    logger.info("Date of birth: 2000-01-01T12:00:00")
    logger.info("Location: 40.7128°N, 74.0060°W")
    
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Calculating birth chart" in log_content
    assert "Date of birth: 2000-01-01T12:00:00" in log_content
    assert "Location: 40.7128°N, 74.0060°W" in log_content

def test_interpretation_logging(tmp_path):
    """Test logging during interpretation generation."""
    log_file = tmp_path / "interpretation.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app.services.interpretation")
    
    # Log a sample interpretation
    logger.info("Generating interpretation")
    logger.info("Level: basic")
    logger.info("Area: general")
    
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Generating interpretation" in log_content
    assert "Level: basic" in log_content
    assert "Area: general" in log_content

def test_error_logging(tmp_path):
    """Test error logging."""
    log_file = tmp_path / "error.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app")
    
    # Log an error
    try:
        raise ValueError("Test error")
    except ValueError as e:
        logger.error(f"Error occurred: {str(e)}")
    
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "ERROR" in log_content
    assert "Error occurred: Test error" in log_content

def test_structured_data_logging(tmp_path):
    """Test logging of structured data loading."""
    log_file = tmp_path / "structured_data.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app.services.interpretation")
    
    # Log structured data loading
    logger.info("Loading structured data")
    logger.info("Loading planets data")
    logger.info("Loading houses data")
    logger.info("Loading aspects data")
    
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Loading structured data" in log_content
    assert "Loading planets data" in log_content
    assert "Loading houses data" in log_content
    assert "Loading aspects data" in log_content

def test_performance_logging(tmp_path):
    """Test performance logging."""
    log_file = tmp_path / "performance.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger("app.services.interpretation")
    
    # Log performance metrics
    logger.info("Performance metrics:")
    logger.info("Birth chart calculation: 0.5s")
    logger.info("Interpretation generation: 1.2s")
    logger.info("Total processing time: 1.7s")
    
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Performance metrics:" in log_content
    assert "Birth chart calculation: 0.5s" in log_content
    assert "Interpretation generation: 1.2s" in log_content
    assert "Total processing time: 1.7s" in log_content

def test_log_rotation(tmp_path):
    """Test log rotation."""
    log_file = tmp_path / "test_rotation.log"
    setup_logging(log_file=str(log_file), max_bytes=1000, backup_count=2)
    logger = get_logger("app")
    
    # Write enough log messages to trigger rotation
    for i in range(100):
        logger.info(f"Test log message {i}")
    
    # Check that rotation files are created
    assert log_file.exists()
    assert not (tmp_path / "test_rotation.log.3").exists()
    assert (tmp_path / "test_rotation.log.1").exists()
    assert (tmp_path / "test_rotation.log.2").exists()

def test_log_formatting(tmp_path):
    # Configure test logging with JSON formatting
    log_file = tmp_path / "test_format.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    
    # Log structured data
    test_data = {
        "event": "test",
        "data": {"key": "value"}
    }
    logger.info(json.dumps(test_data))
    
    # Check log file
    log_content = log_file.read_text()
    assert "test" in log_content
    assert "key" in log_content
    assert "value" in log_content
