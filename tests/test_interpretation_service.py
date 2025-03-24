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
                "degree": 5.0,
                "house": 1
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
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Mercury": {"sign": "Capricorn", "degree": 12.3, "house": 1},
            "Venus": {"sign": "Capricorn", "degree": 8.7, "house": 1},
            "Mars": {"sign": "Leo", "degree": 22.8, "house": 8},
            "Jupiter": {"sign": "Libra", "degree": 195.6, "house": 7},
            "Saturn": {"sign": "Capricorn", "degree": 15.9, "house": 1},
            "Uranus": {"sign": "Capricorn", "degree": 285.9, "house": 10},
            "Neptune": {"sign": "Capricorn", "degree": 290.5, "house": 10},
            "Pluto": {"sign": "Scorpio", "degree": 220.3, "house": 8},
            "Ascendant": {"sign": "Capricorn", "degree": 5.0, "house": 1},
            "Midheaven": {"sign": "Libra", "degree": 195.0, "house": 10}
        },
        "houses": {
            "1": {"sign": "Capricorn", "degree": 5.0},
            "2": {"sign": "Aquarius", "degree": 35.0},
            "3": {"sign": "Pisces", "degree": 65.0},
            "4": {"sign": "Aries", "degree": 95.0},
            "5": {"sign": "Taurus", "degree": 125.0},
            "6": {"sign": "Gemini", "degree": 155.0},
            "7": {"sign": "Cancer", "degree": 185.0},
            "8": {"sign": "Leo", "degree": 215.0},
            "9": {"sign": "Virgo", "degree": 245.0},
            "10": {"sign": "Libra", "degree": 275.0},
            "11": {"sign": "Scorpio", "degree": 305.0},
            "12": {"sign": "Sagittarius", "degree": 335.0}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": "conjunction", "orb": 4.7},
            {"planet1": "Sun", "planet2": "Mercury", "type": "conjunction", "orb": 1.8},
            {"planet1": "Sun", "planet2": "Venus", "type": "conjunction", "orb": 1.8},
            {"planet1": "Sun", "planet2": "Saturn", "type": "conjunction", "orb": 5.4}
        ]
    }
    
    result = interpretation_service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    assert "data" in result
    assert "interpretations" in result["data"]
    assert "planets" in result["data"]["interpretations"]
    assert "houses" in result["data"]["interpretations"]
    assert "aspects" in result["data"]["interpretations"]
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
            "Mercury": {"sign": "Capricorn", "degree": 12.3, "house": 1},
            "Venus": {"sign": "Capricorn", "degree": 8.7, "house": 1},
            "Ascendant": {"sign": "Leo", "degree": 5.8, "house": 1}
        },
        "aspects": []
    }
    
    patterns = interpretation_service._analyze_patterns(birth_chart)
    
    # Check for the correct structure of the patterns dictionary
    assert "t_squares" in patterns
    assert "grand_trines" in patterns
    assert "yods" in patterns
    assert "stelliums" in patterns
    
    # Check for stellium detection
    assert len(patterns["stelliums"]) > 0
    assert patterns["stelliums"][0]["sign"] == "Capricorn"
    assert "Sun" in patterns["stelliums"][0]["planets"]
    assert "Mercury" in patterns["stelliums"][0]["planets"]
    assert "Venus" in patterns["stelliums"][0]["planets"]

def test_analyze_combinations(interpretation_service):
    """Test the _analyze_combinations method."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Mercury": {"sign": "Capricorn", "degree": 12.3, "house": 1},
            "Venus": {"sign": "Aries", "degree": 16.7, "house": 4},
            "Ascendant": {"sign": "Leo", "degree": 5.8, "house": 1}
        },
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "type": 0,
                "orb": 4.7
            }
        ]
    }
    
    combinations = interpretation_service._analyze_combinations(birth_chart)
    
    # Check for the correct structure of the combinations dictionary
    assert "mutual_receptions" in combinations
    assert "planetary_pairs" in combinations
    assert "aspect_patterns" in combinations
    
    # Test special aspects or aspect patterns
    if len(combinations["aspect_patterns"]) > 0:
        pattern = combinations["aspect_patterns"][0]
        assert "type" in pattern
        assert "focal_planet" in pattern or ("planet1" in pattern and "planet2" in pattern)

def test_analyze_house_emphasis(interpretation_service):
    """Test the _analyze_house_emphasis method."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Mercury": {"sign": "Capricorn", "degree": 12.3, "house": 1},
            "Venus": {"sign": "Aries", "degree": 16.7, "house": 4},
            "Mars": {"sign": "Leo", "degree": 22.8, "house": 8},
            "Ascendant": {"sign": "Leo", "degree": 5.8, "house": 1},
            "Midheaven": {"sign": "Aries", "degree": 17.5, "house": 10}
        }
    }
    
    emphasis = interpretation_service._analyze_house_emphasis(birth_chart)
    
    # Check for the correct structure of the house_emphasis dictionary
    assert "counts" in emphasis
    assert "emphasis" in emphasis
    
    # Check that all house types are included
    assert "angular" in emphasis["counts"]
    assert "succedent" in emphasis["counts"]
    assert "cadent" in emphasis["counts"]
    
    # Check that emphasis contains interpretations
    if len(emphasis["emphasis"]) > 0:
        assert "type" in emphasis["emphasis"][0]
        assert "count" in emphasis["emphasis"][0]
        assert "percentage" in emphasis["emphasis"][0]
        assert "planets" in emphasis["emphasis"][0]
        assert "interpretation" in emphasis["emphasis"][0]

def test_get_planet_interpretation(interpretation_service):
    """Test planet interpretation generation."""
    interpretation = interpretation_service._get_planet_interpretation("sun", "capricorn", 1)
    assert "Sun in Capricorn" in interpretation
    assert "represents identity, vitality, ego" in interpretation

def test_get_house_interpretation(interpretation_service):
    """Test house interpretation generation."""
    interpretation = interpretation_service._get_house_interpretation(1, "capricorn")
    assert "House 1 in Capricorn" in interpretation
    assert "represents self, identity, appearance" in interpretation

def test_get_aspect_interpretation(interpretation_service):
    """Test aspect interpretation generation."""
    interpretation = interpretation_service._get_aspect_interpretation(
        planet1="sun",
        planet2="moon",
        aspect_type="conjunction",
        birth_chart={"aspects": [], "planets": []},
        level="basic",
        orb=2.5
    )
    assert "conjunction" in interpretation.lower()
    assert "strong" in interpretation.lower()

def test_get_planet_dignity(interpretation_service):
    """Test the _get_planet_dignity method."""
    dignity = interpretation_service._get_planet_dignity("Sun", "Leo", 1)
    assert isinstance(dignity, dict)
    assert "planet" in dignity
    assert "sign" in dignity
    assert "house" in dignity
    assert "essential_dignity" in dignity
    assert "accidental_dignity" in dignity
    assert "strength" in dignity
    assert "interpretation" in dignity

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

def test_analyze_element_modality_balance(interpretation_service, sample_birth_chart):
    """Test analyzing element and modality balance in the chart."""
    balance = interpretation_service._analyze_element_modality_balance(sample_birth_chart)
    
    assert "counts" in balance
    assert "percentages" in balance
    assert "dominant" in balance
    assert "lacking" in balance
    assert "interpretation" in balance
    
    assert "elements" in balance["counts"]
    assert "modalities" in balance["counts"]
    
    elements = balance["counts"]["elements"]
    modalities = balance["counts"]["modalities"]
    
    assert all(element in elements for element in ["fire", "earth", "air", "water"])
    assert all(modality in modalities for modality in ["cardinal", "fixed", "mutable"])

def test_analyze_quadrant_emphasis(interpretation_service, sample_birth_chart):
    """Test analyzing quadrant emphasis in the chart."""
    emphasis = interpretation_service._analyze_quadrant_emphasis(sample_birth_chart)
    
    assert "counts" in emphasis
    assert "percentages" in emphasis
    assert "dominant" in emphasis
    assert "interpretation" in emphasis
    
    quadrants = emphasis["counts"]
    assert all(quadrant in quadrants for quadrant in ["north", "east", "south", "west"])

def test_planet_interpretation(interpretation_service):
    """Test detailed planet interpretation."""
    interpretation = interpretation_service._get_planet_interpretation("sun", "capricorn", 1, level="detailed")
    assert "Element: Earth" in interpretation
    assert "Modality: Cardinal" in interpretation
    assert "General: ambitious and disciplined" in interpretation

def test_house_interpretation(interpretation_service):
    """Test detailed house interpretation."""
    interpretation = interpretation_service._get_house_interpretation(1, "capricorn", level="detailed")
    assert "Element: Earth" in interpretation
    assert "Modality: Cardinal" in interpretation

def test_aspect_interpretation(interpretation_service):
    """Test aspect interpretation with detailed level."""
    interpretation = interpretation_service._get_aspect_interpretation(
        planet1="sun",
        planet2="moon",
        aspect_type="conjunction",
        birth_chart={"aspects": [], "planets": []},
        level="detailed",
        orb=2.5
    )
    assert "conjunction" in interpretation.lower()
    assert "strong" in interpretation.lower()

def test_combination_interpretations(interpretation_service):
    """Test various combination interpretations."""
    birth_chart = {
        "planets": {
            "Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1},
            "Moon": {"sign": "Aries", "degree": 15.2, "house": 4},
            "Mercury": {"sign": "Sagittarius", "degree": 28.3, "house": 12},
            "Venus": {"sign": "Aquarius", "degree": 5.7, "house": 2},
            "Mars": {"sign": "Aries", "degree": 12.8, "house": 4},
            "Jupiter": {"sign": "Taurus", "degree": 25.5, "house": 5},
            "Saturn": {"sign": "Capricorn", "degree": 15.9, "house": 1},
            "Ascendant": {"sign": "Capricorn", "degree": 2.5, "house": 1},
            "Midheaven": {"sign": "Scorpio", "degree": 280.5, "house": 10}
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Moon", "type": "opposition", "orb": 4.7},
            {"planet1": "Sun", "planet2": "Mars", "type": "opposition", "orb": 2.3},
            {"planet1": "Moon", "planet2": "Mars", "type": "conjunction", "orb": 2.4}
        ]
    }
    
    combinations = interpretation_service._analyze_combinations(birth_chart)
    
    assert "mutual_receptions" in combinations
    assert "planetary_pairs" in combinations
    assert "aspect_patterns" in combinations

def test_special_configuration_details(interpretation_service):
    """Test detection and interpretation of special configurations."""
    birth_chart = {
        "planets": {
            "sun": {"sign": "aries", "degree": 15.5, "house": 1},
            "moon": {"sign": "leo", "degree": 135.8, "house": 5},
            "mercury": {"sign": "sagittarius", "degree": 255.2, "house": 9},
            "venus": {"sign": "cancer", "degree": 105.7, "house": 4},
            "mars": {"sign": "libra", "degree": 195.3, "house": 7},
            "jupiter": {"sign": "capricorn", "degree": 285.6, "house": 10},
            "saturn": {"sign": "cancer", "degree": 100.9, "house": 4},
            "uranus": {"sign": "capricorn", "degree": 290.5, "house": 10},
            "neptune": {"sign": "capricorn", "degree": 295.1, "house": 10},
            "pluto": {"sign": "scorpio", "degree": 220.3, "house": 8},
            "ascendant": {"sign": "aries", "degree": 0.0, "house": 1},
            "midheaven": {"sign": "capricorn", "degree": 270.0, "house": 10}
        },
        "houses": {
            "1": {"sign": "aries", "degree": 0.0},
            "2": {"sign": "taurus", "degree": 30.0},
            "3": {"sign": "gemini", "degree": 60.0},
            "4": {"sign": "cancer", "degree": 90.0},
            "5": {"sign": "leo", "degree": 120.0},
            "6": {"sign": "virgo", "degree": 150.0},
            "7": {"sign": "libra", "degree": 180.0},
            "8": {"sign": "scorpio", "degree": 210.0},
            "9": {"sign": "sagittarius", "degree": 240.0},
            "10": {"sign": "capricorn", "degree": 270.0},
            "11": {"sign": "aquarius", "degree": 300.0},
            "12": {"sign": "pisces", "degree": 330.0}
        },
        "aspects": [
            {"planet1": "sun", "planet2": "moon", "type": "trine", "orb": 0.3},
            {"planet1": "moon", "planet2": "mercury", "type": "trine", "orb": 0.6},
            {"planet1": "sun", "planet2": "mercury", "type": "trine", "orb": 0.3}
        ]
    }
    
    result = interpretation_service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    assert "special_configurations" in result["data"]
    assert "grand_trines" in result["data"]["special_configurations"]
    
    # Check grand trine detection
    grand_trines = result["data"]["special_configurations"]["grand_trines"]
    assert len(grand_trines) > 0
    
    # Check interpretation content
    if len(grand_trines) > 0:
        assert "planets" in grand_trines[0]
        assert "element" in grand_trines[0]
        assert "interpretation" in grand_trines[0]

def test_multiple_configurations(interpretation_service):
    """Test detection of multiple configurations in a complex chart."""
    birth_chart = {
        "planets": {
            "sun": {"sign": "aries", "degree": 15.5, "house": 1},
            "moon": {"sign": "aries", "degree": 10.8, "house": 1},
            "mercury": {"sign": "aries", "degree": 5.2, "house": 1},
            "venus": {"sign": "cancer", "degree": 105.7, "house": 4},
            "mars": {"sign": "libra", "degree": 195.3, "house": 7},
            "jupiter": {"sign": "capricorn", "degree": 285.6, "house": 10},
            "saturn": {"sign": "cancer", "degree": 100.9, "house": 4},
            "uranus": {"sign": "capricorn", "degree": 290.5, "house": 10},
            "neptune": {"sign": "capricorn", "degree": 295.1, "house": 10},
            "pluto": {"sign": "scorpio", "degree": 220.3, "house": 8},
            "ascendant": {"sign": "aries", "degree": 0.0, "house": 1},
            "midheaven": {"sign": "capricorn", "degree": 270.0, "house": 10}
        },
        "houses": {
            "1": {"sign": "aries", "degree": 0.0},
            "2": {"sign": "taurus", "degree": 30.0},
            "3": {"sign": "gemini", "degree": 60.0},
            "4": {"sign": "cancer", "degree": 90.0},
            "5": {"sign": "leo", "degree": 120.0},
            "6": {"sign": "virgo", "degree": 150.0},
            "7": {"sign": "libra", "degree": 180.0},
            "8": {"sign": "scorpio", "degree": 210.0},
            "9": {"sign": "sagittarius", "degree": 240.0},
            "10": {"sign": "capricorn", "degree": 270.0},
            "11": {"sign": "aquarius", "degree": 300.0},
            "12": {"sign": "pisces", "degree": 330.0}
        },
        "aspects": [
            {"planet1": "sun", "planet2": "moon", "type": "conjunction", "orb": 4.7},
            {"planet1": "moon", "planet2": "mercury", "type": "conjunction", "orb": 5.6},
            {"planet1": "sun", "planet2": "mercury", "type": "conjunction", "orb": 10.3},
            {"planet1": "venus", "planet2": "mars", "type": "square", "orb": 0.4},
            {"planet1": "mars", "planet2": "jupiter", "type": "square", "orb": 0.3},
            {"planet1": "jupiter", "planet2": "venus", "type": "square", "orb": 0.1}
        ]
    }
    
    result = interpretation_service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    assert "special_configurations" in result["data"]
    
    # Check stellium detection
    assert "stelliums" in result["data"]["special_configurations"]
    stelliums = result["data"]["special_configurations"]["stelliums"]
    assert len(stelliums) > 0
    assert "planets" in stelliums[0]
    assert "sign" in stelliums[0]
    
    # Check grand cross or t-square detection
    grand_crosses = result["data"]["special_configurations"].get("grand_crosses", [])
    t_squares = result["data"]["special_configurations"].get("t_squares", [])
    assert len(grand_crosses) > 0 or len(t_squares) > 0

def test_configuration_interpretation_format(interpretation_service):
    """Test the interpretation format for configurations."""
    birth_chart = {
        "planets": {
            "sun": {"sign": "Aries", "degree": 15.5, "house": 1},
            "moon": {"sign": "Aries", "degree": 10.8, "house": 1},
            "mercury": {"sign": "Aries", "degree": 5.2, "house": 1},
            "venus": {"sign": "Taurus", "degree": 45.7, "house": 2},
            "mars": {"sign": "Gemini", "degree": 75.3, "house": 3},
            "jupiter": {"sign": "Libra", "degree": 195.6, "house": 7},
            "saturn": {"sign": "Capricorn", "degree": 285.9, "house": 10},
            "uranus": {"sign": "Capricorn", "degree": 290.5, "house": 10},
            "neptune": {"sign": "Capricorn", "degree": 295.1, "house": 10},
            "pluto": {"sign": "Scorpio", "degree": 220.3, "house": 8},
            "ascendant": {"sign": "Aries", "degree": 0.0, "house": 1},
            "midheaven": {"sign": "Capricorn", "degree": 270.0, "house": 10}
        },
        "houses": {
            "1": {"sign": "Aries", "degree": 0.0},
            "2": {"sign": "Taurus", "degree": 30.0},
            "3": {"sign": "Gemini", "degree": 60.0},
            "4": {"sign": "Cancer", "degree": 90.0},
            "5": {"sign": "Leo", "degree": 120.0},
            "6": {"sign": "Virgo", "degree": 150.0},
            "7": {"sign": "Libra", "degree": 180.0},
            "8": {"sign": "Scorpio", "degree": 210.0},
            "9": {"sign": "Sagittarius", "degree": 240.0},
            "10": {"sign": "Capricorn", "degree": 270.0},
            "11": {"sign": "Aquarius", "degree": 300.0},
            "12": {"sign": "Pisces", "degree": 330.0}
        },
        "aspects": [
            {"planet1": "sun", "planet2": "moon", "type": "conjunction", "orb": 4.7},
            {"planet1": "moon", "planet2": "mercury", "type": "conjunction", "orb": 5.6},
            {"planet1": "sun", "planet2": "mercury", "type": "conjunction", "orb": 10.3}
        ]
    }
    
    result = interpretation_service.generate_interpretation(birth_chart=birth_chart)
    
    assert result["status"] == "success"
    
    # Check stellium interpretation format
    stelliums = result["data"]["special_configurations"]["stelliums"]
    if len(stelliums) > 0:
        assert "interpretation" in stelliums[0]
        assert isinstance(stelliums[0]["interpretation"], str)
        assert len(stelliums[0]["interpretation"]) > 0
