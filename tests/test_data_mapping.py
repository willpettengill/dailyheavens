import pytest
import json
from pathlib import Path
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService

@pytest.fixture
def structured_data_dir():
    return Path("data/structured")

@pytest.fixture
def load_structured_data(structured_data_dir):
    data = {}
    for file in structured_data_dir.glob("*.json"):
        with open(file, "r") as f:
            data[file.stem] = json.load(f)
    return data

def test_planet_sign_mapping(interpretation_service):
    """Test planet-sign mapping data."""
    planets_data = interpretation_service.planets_data
    assert "sun" in planets_data
    assert "qualities" in planets_data["sun"]
    assert "general" in planets_data["sun"]["qualities"]

def test_house_sign_mapping(interpretation_service):
    """Test house-sign mapping data."""
    house_data = interpretation_service.house_data
    assert "1" in house_data
    assert "basic_meaning" in house_data["1"]
    assert "detailed_meaning" in house_data["1"]

def test_aspect_mapping(interpretation_service):
    """Test aspect mapping data."""
    aspect_data = interpretation_service.aspect_data
    assert "conjunction" in aspect_data
    assert "description" in aspect_data["conjunction"]
    assert "interpretation" in aspect_data["conjunction"]

def test_interpretation_template_mapping(interpretation_service):
    """Test interpretation template mapping."""
    templates = interpretation_service.templates
    assert "planet_interpretations" in templates
    assert "house_interpretations" in templates
    assert "aspect_interpretations" in templates

def test_dignity_mapping(interpretation_service):
    """Test dignity mapping data."""
    dignities_data = interpretation_service.dignities_data
    assert "planets" in dignities_data
    assert "relationships" in dignities_data
    assert "combustion" in dignities_data
    assert "retrograde" in dignities_data
    
    # Test planet data
    sun_data = dignities_data["planets"]["Sun"]
    assert "rulership" in sun_data
    assert "exaltation" in sun_data
    assert "detriment" in sun_data
    assert "fall" in sun_data
    assert "joy" in sun_data
    assert "triplicity" in sun_data
    assert "terms" in sun_data
    assert "face" in sun_data
    
    # Test relationships
    relationships = dignities_data["relationships"]
    assert "friendships" in relationships
    assert "enmities" in relationships
    assert "neutral" in relationships
    
    # Test combustion
    combustion = dignities_data["combustion"]
    assert "description" in combustion
    assert "orb" in combustion
    
    # Test retrograde
    retrograde = dignities_data["retrograde"]
    assert "description" in retrograde
    assert "frequency" in retrograde

def test_technique_mapping(interpretation_service):
    """Test technique mapping data."""
    techniques = interpretation_service.techniques
    assert "aspect_patterns" in techniques
    assert "house_systems" in techniques

def test_description_mapping(interpretation_service):
    """Test mapping of astrological descriptions."""
    descriptions = interpretation_service.descriptions
    for sign in ["aries", "taurus", "gemini", "cancer", "leo", "virgo", 
                 "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]:
        assert sign in descriptions
        assert "sun_sign" in descriptions[sign]
        assert "moon_sign" in descriptions[sign]
        assert "rising_sign" in descriptions[sign]
