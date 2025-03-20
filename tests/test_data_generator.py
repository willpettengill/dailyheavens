import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.models.interpretation import InterpretationArea, InterpretationLevel

class TestDataGenerator:
    """Generates systematic test data for astrological combinations."""
    
    # All possible zodiac signs
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    # All possible planets
    PLANETS = [
        "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
        "Saturn", "Uranus", "Neptune", "Pluto"
    ]
    
    # All possible houses
    HOUSES = [str(i) for i in range(1, 13)]
    
    # All possible aspects
    ASPECTS = [
        "conjunction", "opposition", "trine", "square", "sextile",
        "semisextile", "semisquare", "sesquisquare", "quincunx"
    ]
    
    @classmethod
    def generate_birth_chart(cls, 
                           sun_sign: str = None,
                           moon_sign: str = None,
                           asc_sign: str = None,
                           house_1_sign: str = None) -> Dict[str, Any]:
        """Generate a birth chart with specified placements."""
        chart = {
            "planets": {},
            "houses": {},
            "angles": {}
        }
        
        # Generate planet placements
        for planet in cls.PLANETS:
            if planet == "Sun" and sun_sign:
                chart["planets"][planet] = {
                    "sign": sun_sign,
                    "degree": 15.0,
                    "house": 1
                }
            elif planet == "Moon" and moon_sign:
                chart["planets"][planet] = {
                    "sign": moon_sign,
                    "degree": 15.0,
                    "house": 4
                }
            else:
                chart["planets"][planet] = {
                    "sign": cls.SIGNS[0],
                    "degree": 15.0,
                    "house": 1
                }
        
        # Generate house placements
        for house in cls.HOUSES:
            if house == "1" and house_1_sign:
                chart["houses"][house] = {
                    "sign": house_1_sign,
                    "degree": 0.0
                }
            else:
                chart["houses"][house] = {
                    "sign": cls.SIGNS[0],
                    "degree": 0.0
                }
        
        # Generate angle placements
        if asc_sign:
            chart["angles"]["Asc"] = {
                "sign": asc_sign,
                "degree": 0.0
            }
        else:
            chart["angles"]["Asc"] = {
                "sign": cls.SIGNS[0],
                "degree": 0.0
            }
        
        return chart
    
    @classmethod
    def generate_sign_combinations(cls) -> List[Dict[str, Any]]:
        """Generate all possible combinations of Sun, Moon, and Ascendant signs."""
        combinations = []
        for sun_sign in cls.SIGNS:
            for moon_sign in cls.SIGNS:
                for asc_sign in cls.SIGNS:
                    chart = cls.generate_birth_chart(
                        sun_sign=sun_sign,
                        moon_sign=moon_sign,
                        asc_sign=asc_sign,
                        house_1_sign=asc_sign
                    )
                    combinations.append(chart)
        return combinations
    
    @classmethod
    def generate_house_placements(cls) -> List[Dict[str, Any]]:
        """Generate test cases for all possible house placements."""
        placements = []
        for planet in cls.PLANETS:
            for house in cls.HOUSES:
                chart = cls.generate_birth_chart()
                chart["planets"][planet]["house"] = house
                placements.append(chart)
        return placements
    
    @classmethod
    def generate_aspect_patterns(cls) -> List[Dict[str, Any]]:
        """Generate test cases for different aspect patterns."""
        patterns = []
        for aspect in cls.ASPECTS:
            chart = cls.generate_birth_chart()
            # Add aspect information
            chart["aspects"] = {
                f"{cls.PLANETS[0]}-{cls.PLANETS[1]}": {
                    "type": aspect,
                    "degree": 0.0
                }
            }
            patterns.append(chart)
        return patterns
    
    @classmethod
    def generate_interpretation_requests(cls) -> List[Dict[str, Any]]:
        """Generate test cases for all interpretation combinations."""
        requests = []
        chart = cls.generate_birth_chart()
        
        for area in InterpretationArea:
            for level in InterpretationLevel:
                request = {
                    "birth_chart": chart,
                    "area": area.value,
                    "level": level.value
                }
                requests.append(request)
        return requests
    
    @classmethod
    def generate_edge_cases(cls) -> List[Dict[str, Any]]:
        """Generate test cases for edge cases."""
        edge_cases = []
        
        # Test cusps
        for sign in cls.SIGNS:
            chart = cls.generate_birth_chart()
            chart["planets"]["Sun"]["degree"] = 29.9  # Late degree
            chart["planets"]["Sun"]["sign"] = sign
            edge_cases.append(chart)
        
        # Test retrograde planets
        for planet in cls.PLANETS:
            if planet in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
                chart = cls.generate_birth_chart()
                chart["planets"][planet]["retrograde"] = True
                edge_cases.append(chart)
        
        # Test intercepted signs
        chart = cls.generate_birth_chart()
        chart["houses"]["1"]["intercepted_signs"] = ["Aries", "Taurus"]
        edge_cases.append(chart)
        
        return edge_cases 