import pytest
from app.services.interpretation import InterpretationService
from app.models.interpretation import InterpretationArea, InterpretationLevel

@pytest.fixture
def sample_birth_chart():
    return {
        "planets": {
            "Sun": {
                "sign": "Capricorn",
                "degree": 10.5,
                "house": 1
            },
            "Moon": {
                "sign": "Aries",
                "degree": 15.2,
                "house": 4
            },
            "Mars": {
                "sign": "Leo",
                "degree": 22.8,
                "house": 8
            },
            "Ascendant": {
                "sign": "Capricorn",
                "degree": 5.0
            }
        },
        "houses": {
            "1": {
                "sign": "Capricorn",
                "degree": 5.0
            },
            "4": {
                "sign": "Aries",
                "degree": 15.0
            },
            "8": {
                "sign": "Leo",
                "degree": 22.0
            }
        },
        "angles": {
            "ASC": {
                "sign": "Capricorn",
                "degree": 5.0
            },
            "MC": {
                "sign": "Libra",
                "degree": 15.0
            }
        },
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "type": "conjunction",
                "orb": 4.7
            }
        ]
    }

@pytest.fixture
def interpretation_service():
    return InterpretationService()

def test_generate_interpretation(interpretation_service):
    """Test the generate_interpretation method."""
    result = interpretation_service.generate_interpretation(
        date_of_birth="1990-01-01",
        latitude=40.7128,
        longitude=-74.0060,
        level="basic",
        area="general"
    )
    
    assert result["status"] == "success"
    assert "data" in result
    assert "interpretations" in result["data"]
    assert "aspect_interpretations" in result["data"]
    assert "house_interpretations" in result["data"]
    assert "patterns" in result["data"]
    assert "combinations" in result["data"]
    assert "house_emphasis" in result["data"]
    assert "special_configurations" in result["data"]

def test_analyze_patterns(interpretation_service):
    """Test the _analyze_patterns method."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Ascendant": {"sign": "Leo", "degree": 5.8}
        }
    }
    
    patterns = interpretation_service._analyze_patterns(birth_chart)
    
    assert "element_distribution" in patterns
    assert "modality_distribution" in patterns
    assert all(element in patterns["element_distribution"] for element in ["fire", "earth", "air", "water"])
    assert all(modality in patterns["modality_distribution"] for modality in ["cardinal", "fixed", "mutable"])

def test_analyze_combinations(interpretation_service):
    """Test the _analyze_combinations method."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Ascendant": {"sign": "Leo", "degree": 5.8}
        }
    }
    
    combinations = interpretation_service._analyze_combinations(birth_chart)
    
    assert "sun_moon" in combinations
    assert "sun_rising" in combinations
    assert "moon_rising" in combinations
    assert "interpretation" in combinations["sun_moon"]
    assert "interpretation" in combinations["sun_rising"]
    assert "interpretation" in combinations["moon_rising"]

def test_analyze_house_emphasis(interpretation_service):
    """Test the _analyze_house_emphasis method."""
    birth_chart = {
        "houses": {
            "1": {"sign": "Leo", "degree": 5.8},
            "4": {"sign": "Scorpio", "degree": 15.2},
            "10": {"sign": "Taurus", "degree": 5.8}
        }
    }
    
    emphasis = interpretation_service._analyze_house_emphasis(birth_chart)
    
    assert "counts" in emphasis
    assert "dominant" in emphasis
    assert "interpretation" in emphasis
    assert all(quadrant in emphasis["counts"] for quadrant in ["angular", "succedent", "cadent"])

def test_get_planet_interpretation(interpretation_service):
    """Test the _get_planet_interpretation method."""
    interpretation = interpretation_service._get_planet_interpretation("Sun", "Capricorn")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Capricorn" in interpretation

def test_get_house_interpretation(interpretation_service):
    """Test the _get_house_interpretation method."""
    interpretation = interpretation_service._get_house_interpretation("1", "Leo")
    assert isinstance(interpretation, str)
    assert "House 1" in interpretation
    assert "Leo" in interpretation

def test_get_aspect_interpretation(interpretation_service):
    """Test the _get_aspect_interpretation method."""
    interpretation = interpretation_service._get_aspect_interpretation("Sun", "Moon", "conjunction")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Moon" in interpretation
    assert "conjunction" in interpretation

def test_get_planet_dignity(interpretation_service):
    """Test the _get_planet_dignity method."""
    dignity = interpretation_service._get_planet_dignity("Sun", "Leo")
    assert isinstance(dignity, str)
    assert dignity in ["rulership", "exaltation", "detriment", "fall", "neutral"]

def test_get_sun_moon_combination_interpretation(interpretation_service):
    """Test the _get_sun_moon_combination_interpretation method."""
    interpretation = interpretation_service._get_sun_moon_combination_interpretation("Capricorn", "Aries")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Moon" in interpretation
    assert "Capricorn" in interpretation
    assert "Aries" in interpretation

def test_get_sun_rising_combination_interpretation(interpretation_service):
    """Test the _get_sun_rising_combination_interpretation method."""
    interpretation = interpretation_service._get_sun_rising_combination_interpretation("Capricorn", "Leo")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Ascendant" in interpretation
    assert "Capricorn" in interpretation
    assert "Leo" in interpretation

def test_get_moon_rising_combination_interpretation(interpretation_service):
    """Test the _get_moon_rising_combination_interpretation method."""
    interpretation = interpretation_service._get_moon_rising_combination_interpretation("Aries", "Leo")
    assert isinstance(interpretation, str)
    assert "Moon" in interpretation
    assert "Ascendant" in interpretation
    assert "Aries" in interpretation
    assert "Leo" in interpretation

def test_error_handling(interpretation_service):
    """Test error handling in interpretation generation."""
    # Test with empty birth chart
    result = interpretation_service.generate_interpretation({})
    assert result["status"] == "error"
    assert "message" in result
    
    # Test with invalid planet data
    result = interpretation_service.generate_interpretation({"planets": {"InvalidPlanet": {}}})
    assert result["status"] == "error"
    assert "message" in result

def test_analyze_elemental_patterns(interpretation_service, sample_birth_chart):
    """Test analyzing elemental patterns in the chart."""
    patterns = interpretation_service._analyze_patterns(sample_birth_chart)
    assert "counts" in patterns
    assert "dominant" in patterns
    assert "element_distribution" in patterns
    assert "interpretation" in patterns

def test_analyze_modality_patterns(interpretation_service, sample_birth_chart):
    """Test analyzing modality patterns in the chart."""
    patterns = interpretation_service._analyze_patterns(sample_birth_chart)
    assert "counts" in patterns
    assert "dominant" in patterns
    assert "modality_distribution" in patterns
    assert "interpretation" in patterns

def test_analyze_sun_moon_combination(interpretation_service, sample_birth_chart):
    """Test analyzing Sun-Moon combination."""
    combination = interpretation_service._analyze_combinations(sample_birth_chart)
    assert "sun_moon" in combination
    assert "interpretation" in combination["sun_moon"]
    assert "strength" in combination["sun_moon"]

def test_analyze_sun_rising_combination(interpretation_service, sample_birth_chart):
    """Test analyzing Sun-Rising combination."""
    combination = interpretation_service._analyze_combinations(sample_birth_chart)
    assert "sun_rising" in combination
    assert "interpretation" in combination["sun_rising"]
    assert "strength" in combination["sun_rising"]

def test_analyze_moon_rising_combination(interpretation_service, sample_birth_chart):
    """Test analyzing Moon-Rising combination."""
    combination = interpretation_service._analyze_combinations(sample_birth_chart)
    assert "moon_rising" in combination
    assert "interpretation" in combination["moon_rising"]
    assert "strength" in combination["moon_rising"]

def test_analyze_house_emphasis(interpretation_service, sample_birth_chart):
    """Test analyzing house emphasis in the chart."""
    emphasis = interpretation_service._analyze_house_emphasis(sample_birth_chart)
    assert "dominant_houses" in emphasis
    assert "interpretation" in emphasis
    assert "strength" in emphasis

def test_get_planet_interpretation(interpretation_service):
    """Test getting planet interpretation."""
    interpretation = interpretation_service._get_planet_interpretation("Sun", "Aries", 1)
    assert interpretation is not None
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

def test_get_aspect_interpretation(interpretation_service):
    """Test getting aspect interpretation."""
    interpretation = interpretation_service._get_aspect_interpretation("Sun", "Moon", "conjunction")
    assert interpretation is not None
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

def test_get_house_interpretation(interpretation_service):
    """Test getting house interpretation."""
    interpretation = interpretation_service._get_house_interpretation(1, "Aries")
    assert interpretation is not None
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

def test_planet_interpretation(interpretation_service):
    """Test planet interpretation generation."""
    # Test basic interpretation
    interpretation = interpretation_service._get_planet_interpretation("Sun", "Capricorn")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Capricorn" in interpretation
    assert "qualities" in interpretation.lower()
    
    # Test detailed interpretation
    detailed = interpretation_service._get_planet_interpretation("Moon", "Aries", "detailed")
    assert "element" in detailed.lower()
    assert "modality" in detailed.lower()
    assert "career" in detailed.lower()
    assert "relationships" in detailed.lower()

def test_house_interpretation(interpretation_service):
    """Test house interpretation generation."""
    # Test basic interpretation
    interpretation = interpretation_service._get_house_interpretation("1", "Capricorn")
    assert isinstance(interpretation, str)
    assert "House 1" in interpretation
    assert "Capricorn" in interpretation
    assert "qualities" in interpretation.lower()
    
    # Test detailed interpretation
    detailed = interpretation_service._get_house_interpretation("4", "Aries", "detailed")
    assert "element" in detailed.lower()
    assert "modality" in detailed.lower()
    assert "career" in detailed.lower()
    assert "relationships" in detailed.lower()
    
    # Test invalid house number
    invalid = interpretation_service._get_house_interpretation("invalid", "Aries")
    assert invalid == ""

def test_aspect_interpretation(interpretation_service):
    """Test aspect interpretation generation."""
    # Test basic interpretation
    interpretation = interpretation_service._get_aspect_interpretation("Sun", "Moon", "conjunction")
    assert isinstance(interpretation, str)
    assert "Sun" in interpretation
    assert "Moon" in interpretation
    assert "conjunction" in interpretation
    assert "nature" in interpretation.lower()
    
    # Test detailed interpretation
    detailed = interpretation_service._get_aspect_interpretation("Sun", "Moon", "conjunction", orb=4.7, level="detailed")
    assert "keywords" in detailed.lower()
    assert "orb" in detailed.lower()
    assert "qualities" in detailed.lower()
    
    # Test invalid aspect
    invalid = interpretation_service._get_aspect_interpretation("Invalid", "Moon", "conjunction")
    assert invalid == ""

def test_generate_interpretation(interpretation_service, sample_birth_chart):
    """Test complete interpretation generation."""
    # Test basic interpretation
    result = interpretation_service.generate_interpretation(sample_birth_chart)
    assert result["status"] == "success"
    assert "data" in result
    assert "planets" in result["data"]
    assert "houses" in result["data"]
    assert "aspects" in result["data"]
    
    # Test detailed interpretation
    detailed = interpretation_service.generate_interpretation(
        sample_birth_chart,
        level="detailed",
        area="relationships"
    )
    assert detailed["status"] == "success"
    assert "data" in detailed
    assert "interpretations" in detailed["data"]
    
    # Test error handling
    error_result = interpretation_service.generate_interpretation({})
    assert error_result["status"] == "error"
    assert "message" in error_result

def test_combination_interpretations(interpretation_service):
    """Test combination interpretation generation."""
    # Test Sun-Moon combination
    sun_moon = interpretation_service._get_sun_moon_combination_interpretation("Capricorn", "Aries")
    assert isinstance(sun_moon, str)
    assert "Sun" in sun_moon
    assert "Moon" in sun_moon
    assert "qualities" in sun_moon.lower()
    
    # Test Sun-Rising combination
    sun_rising = interpretation_service._get_sun_rising_combination_interpretation("Capricorn", "Capricorn")
    assert isinstance(sun_rising, str)
    assert "Sun" in sun_rising
    assert "Rising" in sun_rising
    assert "qualities" in sun_rising.lower()
    
    # Test Moon-Rising combination
    moon_rising = interpretation_service._get_moon_rising_combination_interpretation("Aries", "Capricorn")
    assert isinstance(moon_rising, str)
    assert "Moon" in moon_rising
    assert "Rising" in moon_rising
    assert "qualities" in moon_rising.lower()

def test_error_handling(interpretation_service):
    """Test error handling in interpretation generation."""
    # Test with empty birth chart
    result = interpretation_service.generate_interpretation({})
    assert result["status"] == "error"
    assert "message" in result
    
    # Test with invalid planet data
    result = interpretation_service.generate_interpretation({"planets": {"InvalidPlanet": {}}})
    assert result["status"] == "error"
    assert "message" in result
    
    # Test with invalid house data
    result = interpretation_service.generate_interpretation({"houses": {"invalid": {}}})
    assert result["status"] == "error"
    assert "message" in result
    
    # Test with invalid aspect data
    result = interpretation_service.generate_interpretation({"aspects": [{"invalid": "data"}]})
    assert result["status"] == "error"
    assert "message" in result

def test_special_configuration_details():
    """Test detailed information in special configurations."""
    # Create a birth chart with a T-square
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Aries", "degree": 10},
            "Moon": {"sign": "Libra", "degree": 10},
            "Mars": {"sign": "Capricorn", "degree": 10}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": 180},
            {"planet1": "Sun", "planet2": "Mars", "type": 90},
            {"planet1": "Moon", "planet2": "Mars", "type": 90}
        ]
    }
    
    service = InterpretationService()
    result = service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    configs = result["data"]["special_configurations"]["configurations"]
    
    # Check T-square details
    assert "t_square" in configs
    t_square = configs["t_square"][0]
    assert "apex" in t_square
    assert "base" in t_square
    assert len(t_square["base"]) == 2
    assert len(t_square["aspects"]) == 3

def test_multiple_configurations():
    """Test handling of multiple configurations of the same type."""
    # Create a birth chart with multiple grand trines
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Aries", "degree": 10},
            "Moon": {"sign": "Leo", "degree": 10},
            "Mars": {"sign": "Sagittarius", "degree": 10},
            "Venus": {"sign": "Taurus", "degree": 10},
            "Jupiter": {"sign": "Virgo", "degree": 10},
            "Saturn": {"sign": "Capricorn", "degree": 10}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": 120},
            {"planet1": "Moon", "planet2": "Mars", "type": 120},
            {"planet1": "Sun", "planet2": "Mars", "type": 120},
            {"planet1": "Venus", "planet2": "Jupiter", "type": 120},
            {"planet1": "Jupiter", "planet2": "Saturn", "type": 120},
            {"planet1": "Venus", "planet2": "Saturn", "type": 120}
        ]
    }
    
    service = InterpretationService()
    result = service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    configs = result["data"]["special_configurations"]["configurations"]
    
    # Check for multiple grand trines
    assert "grand_trine" in configs
    assert len(configs["grand_trine"]) == 2
    
    # Check interpretation format
    interpretation = result["data"]["special_configurations"]["interpretation"]
    assert "Grand Trine:" in interpretation
    assert interpretation.count("Grand Trine") == 2

def test_configuration_interpretation_format():
    """Test the formatting of configuration interpretations."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Aries", "degree": 10},
            "Moon": {"sign": "Leo", "degree": 10},
            "Mars": {"sign": "Sagittarius", "degree": 10}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": 120},
            {"planet1": "Moon", "planet2": "Mars", "type": 120},
            {"planet1": "Sun", "planet2": "Mars", "type": 120}
        ]
    }
    
    service = InterpretationService()
    result = service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    interpretation = result["data"]["special_configurations"]["interpretation"]
    
    # Check format
    assert "Grand Trine" in interpretation
    assert "Sun, Moon, Mars" in interpretation
    assert "harmonious flow of energy" in interpretation.lower()
