from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.models.interpretation import InterpretationRequest, InterpretationResponse
import logging
from functools import lru_cache
from app.models.astrology import (
    Planet, Sign, House, Aspect, AspectType,
    Element, Modality, Dignity, HouseType
)
from app.services.birth_chart import BirthChartService

logger = logging.getLogger(__name__)

class InterpretationService:
    def __init__(self):
        logger.info("Initializing InterpretationService")
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "structured"
        self._load_structured_data()
        self.birth_chart_service = BirthChartService()
        
        # Initialize data structures
        self.planets_data = {
            "sun": {
                "qualities": {
                    "general": "leadership and vitality",
                    "career": "ambition and authority",
                    "relationships": "romance and partnership",
                    "health": "vitality and energy",
                    "spirituality": "consciousness and purpose",
                    "personal_growth": "identity and self-expression"
                }
            },
            "moon": {
                "qualities": {
                    "general": "emotions and instincts",
                    "career": "emotional satisfaction",
                    "relationships": "emotional needs",
                    "health": "emotional well-being",
                    "spirituality": "intuition and receptivity",
                    "personal_growth": "emotional awareness"
                }
            }
        }
        
        self.houses_data = {
            "1": {
                "qualities": {
                    "general": "self-expression and personality",
                    "career": "leadership style",
                    "relationships": "approach to relationships",
                    "health": "physical vitality",
                    "spirituality": "spiritual identity",
                    "personal_growth": "self-awareness"
                }
            },
            "10": {
                "qualities": {
                    "general": "career and public image",
                    "career": "professional goals",
                    "relationships": "public partnerships",
                    "health": "public health",
                    "spirituality": "spiritual authority",
                    "personal_growth": "life purpose"
                }
            }
        }
        
        self.signs_data = {
            "Aries": {
                "element": "fire",
                "modality": "cardinal",
                "qualities": {
                    "general": "pioneering and assertive",
                    "career": "leadership and initiative",
                    "relationships": "passion and independence",
                    "health": "vitality and energy",
                    "spirituality": "spiritual courage",
                    "personal_growth": "self-assertion"
                },
                "compatible_signs": ["Leo", "Sagittarius", "Gemini", "Libra"]
            },
            "Capricorn": {
                "element": "earth",
                "modality": "cardinal",
                "qualities": {
                    "general": "ambitious and practical",
                    "career": "professional success",
                    "relationships": "stability and commitment",
                    "health": "physical endurance",
                    "spirituality": "material spirituality",
                    "personal_growth": "self-discipline"
                },
                "compatible_signs": ["Taurus", "Virgo", "Scorpio", "Pisces"]
            }
        }

        # Cache for frequently accessed data
        self._sign_cache = {}
        self._planet_cache = {}
        self._aspect_cache = {}
        self._house_cache = {}
        
        # Pre-compute common combinations
        self._element_modality_cache = {}
        self._initialize_caches()
        logger.info("InterpretationService initialized successfully")

    def _initialize_caches(self):
        """Initialize all caches with pre-computed data."""
        # Cache sign data
        for sign in Sign:
            self._sign_cache[sign.name.lower()] = {
                'element': sign.element,
                'modality': sign.modality,
                'qualities': sign.qualities,
                'keywords': sign.keywords
            }
        
        # Cache planet data
        for planet in Planet:
            self._planet_cache[planet.name.lower()] = {
                'qualities': planet.qualities,
                'keywords': planet.keywords,
                'dignities': planet.dignities
            }
        
        # Cache aspect data
        for aspect in AspectType:
            self._aspect_cache[aspect.name.lower()] = {
                'nature': aspect.nature,
                'type': aspect.type,
                'keywords': aspect.keywords
            }
        
        # Cache house data
        for house_num in range(1, 13):
            self._house_cache[str(house_num)] = {
                'type': HouseType.get_type(house_num),
                'qualities': House.get_qualities(house_num),
                'keywords': House.get_keywords(house_num)
            }
        
        # Pre-compute element-modality combinations
        for element in Element:
            for modality in Modality:
                key = f"{element.name.lower()}_{modality.name.lower()}"
                self._element_modality_cache[key] = {
                    'qualities': self._get_element_modality_qualities(element, modality),
                    'keywords': self._get_element_modality_keywords(element, modality)
                }

    def _load_structured_data(self):
        """Load all structured data files."""
        try:
            logger.info("Loading structured data files")
            # Load core data files
            with open(self.data_dir / "planets.json") as f:
                self.planets_data = json.load(f)
            with open(self.data_dir / "houses.json") as f:
                self.houses_data = json.load(f)
            with open(self.data_dir / "aspects.json") as f:
                self.aspects_data = json.load(f)
            with open(self.data_dir / "signs.json") as f:
                self.signs_data = json.load(f)
            with open(self.data_dir / "dignities.json") as f:
                self.dignities_data = json.load(f)
            with open(self.data_dir / "templates.json") as f:
                self.templates = json.load(f)
            
            # Initialize interpretation templates
            self.planet_interpretations = self.templates.get("planet_interpretations", {})
            self.house_interpretations = self.templates.get("house_interpretations", {})
            self.aspect_interpretations = self.templates.get("aspect_interpretations", {})
            self.pattern_interpretations = self.templates.get("pattern_interpretations", {})
            self.combination_interpretations = self.templates.get("combination_interpretations", {})
            
            # Add required attributes for test compatibility
            self.techniques = {
                "aspect_patterns": {
                    "grand_trine": "Three planets in trine aspect",
                    "t_square": "Three planets forming a T-square",
                    "grand_cross": "Four planets in square aspects",
                    "yod": "Two planets in sextile with both quincunx to a third",
                    "stellium": "Three or more planets in conjunction"
                },
                "house_systems": {
                    "placidus": "Most commonly used house system",
                    "equal": "Equal house system",
                    "whole_sign": "Whole sign houses",
                    "koch": "Koch house system",
                    "campanus": "Campanus house system"
                }
            }
            
            self.descriptions = {}
            for sign in ["aries", "taurus", "gemini", "cancer", "leo", "virgo", 
                        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]:
                self.descriptions[sign] = {
                    "sun_sign": self.signs_data.get(sign, {}).get("description", ""),
                    "moon_sign": self.signs_data.get(sign, {}).get("moon_description", ""),
                    "rising_sign": self.signs_data.get(sign, {}).get("rising_description", "")
                }
            
            # Add house_data and aspect_data for test compatibility
            self.house_data = {
                str(i): {
                    "basic_meaning": self.houses_data.get(str(i), {}).get("qualities", {}).get("general", ""),
                    "detailed_meaning": self.houses_data.get(str(i), {}).get("description", ""),
                    "keywords": self.houses_data.get(str(i), {}).get("keywords", []),
                    "ruling_planet": self.houses_data.get(str(i), {}).get("ruler", "")
                }
                for i in range(1, 13)
            }
            
            self.aspect_data = {
                name: {
                    "description": data.get("interpretation", {}).get("general", ""),
                    "keywords": data.get("keywords", []),
                    "nature": data.get("nature", ""),
                    "type": data.get("type", ""),
                    "orb": data.get("orb", 0)
                }
                for name, data in self.aspects_data.items()
            }
            
            # Normalize all keys to lowercase for case-insensitive lookups
            self.planets_data = {k.lower(): v for k, v in self.planets_data.items()}
            self.houses_data = {k.lower(): v for k, v in self.houses_data.items()}
            self.signs_data = {k.lower(): v for k, v in self.signs_data.items()}
            self.aspects_data = {k.lower(): v for k, v in self.aspects_data.items()}
            self.dignities_data = {k.lower(): v for k, v in self.dignities_data.items()}
            
            logger.info("Successfully loaded all structured data files")
        except FileNotFoundError as e:
            logger.error(f"Failed to load structured data file: {e}")
            raise RuntimeError("Failed to initialize interpretation service: missing required data files")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured data file: {e}")
            raise RuntimeError("Failed to initialize interpretation service: invalid data file format")

    def _validate_birth_chart(self, birth_chart: Dict) -> bool:
        """Validate birth chart data structure and content."""
        try:
            # Check required top-level keys
            required_keys = ["planets", "houses"]
            if not all(key in birth_chart for key in required_keys):
                logger.warning("Missing required birth chart keys")
                return False
            
            # Validate planets
            planets = birth_chart.get("planets", {})
            if not planets:
                logger.warning("No planets found in birth chart")
                return False
            
            # Check required planets
            required_planets = ["Sun", "Moon", "Ascendant"]
            missing_planets = [p for p in required_planets if p not in planets]
            if missing_planets:
                logger.warning(f"Missing required planets: {missing_planets}")
                return False
            
            # Validate planet data
            for planet, data in planets.items():
                if not isinstance(data, dict):
                    logger.warning(f"Invalid planet data format for {planet}")
                    return False
                
                required_planet_fields = ["sign", "degree"]
                if not all(field in data for field in required_planet_fields):
                    logger.warning(f"Missing required fields for planet {planet}")
                    return False
                
                # Validate sign
                if data["sign"] not in self.signs_data:
                    logger.warning(f"Invalid sign {data['sign']} for planet {planet}")
                    return False
                
                # Validate degree
                try:
                    degree = float(data["degree"])
                    if not 0 <= degree < 360:
                        logger.warning(f"Invalid degree {degree} for planet {planet}")
                        return False
                except (ValueError, TypeError):
                    logger.warning(f"Invalid degree format for planet {planet}")
                    return False
            
            # Validate houses
            houses = birth_chart.get("houses", {})
            if not houses:
                logger.warning("No houses found in birth chart")
                return False
            
            # Check required houses
            required_houses = ["1", "4", "7", "10"]  # Angular houses
            missing_houses = [h for h in required_houses if h not in houses]
            if missing_houses:
                logger.warning(f"Missing required houses: {missing_houses}")
                return False
            
            # Validate house data
            for house, data in houses.items():
                if not isinstance(data, dict):
                    logger.warning(f"Invalid house data format for house {house}")
                    return False
                
                required_house_fields = ["sign", "degree"]
                if not all(field in data for field in required_house_fields):
                    logger.warning(f"Missing required fields for house {house}")
                    return False
                
                # Validate sign
                if data["sign"] not in self.signs_data:
                    logger.warning(f"Invalid sign {data['sign']} for house {house}")
                    return False
                
                # Validate degree
                try:
                    degree = float(data["degree"])
                    if not 0 <= degree < 360:
                        logger.warning(f"Invalid degree {degree} for house {house}")
                        return False
                except (ValueError, TypeError):
                    logger.warning(f"Invalid degree format for house {house}")
                    return False
            
            # Validate aspects if present
            aspects = birth_chart.get("aspects", [])
            if aspects:
                for aspect in aspects:
                    if not isinstance(aspect, dict):
                        logger.warning("Invalid aspect data format")
                        return False
                    
                    required_aspect_fields = ["planet1", "planet2", "type"]
                    if not all(field in aspect for field in required_aspect_fields):
                        logger.warning("Missing required fields in aspect")
                        return False
                    
                    # Validate planets exist
                    if aspect["planet1"] not in planets or aspect["planet2"] not in planets:
                        logger.warning(f"Invalid planet in aspect: {aspect['planet1']}-{aspect['planet2']}")
                        return False
                    
                    # Validate aspect type
                    if aspect["type"] not in self.aspects_data:
                        logger.warning(f"Invalid aspect type: {aspect['type']}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating birth chart: {str(e)}", exc_info=True)
            return False

    def _validate_interpretation_request(self, request: Dict) -> tuple[bool, str]:
        """Validate interpretation request parameters."""
        try:
            # Check required fields
            if not request.get("birth_chart") and not all(request.get(field) for field in ["date_of_birth", "latitude", "longitude"]):
                return False, "Either birth_chart or date_of_birth, latitude, and longitude must be provided"
            
            # Validate date_of_birth if provided
            if request.get("date_of_birth"):
                try:
                    datetime.fromisoformat(request["date_of_birth"].replace("Z", "+00:00"))
                except ValueError:
                    return False, "Invalid date_of_birth format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            
            # Validate coordinates if provided
            if request.get("latitude") is not None:
                try:
                    lat = float(request["latitude"])
                    if not -90 <= lat <= 90:
                        return False, "Latitude must be between -90 and 90 degrees"
                except (ValueError, TypeError):
                    return False, "Invalid latitude format"
            
            if request.get("longitude") is not None:
                try:
                    lon = float(request["longitude"])
                    if not -180 <= lon <= 180:
                        return False, "Longitude must be between -180 and 180 degrees"
                except (ValueError, TypeError):
                    return False, "Invalid longitude format"
            
            # Validate level
            if request.get("level") not in ["basic", "detailed", None]:
                return False, "Invalid interpretation level. Must be 'basic' or 'detailed'"
            
            # Validate area
            valid_areas = ["general", "career", "relationships", "health", "spirituality", "personal_growth"]
            if request.get("area") not in valid_areas + [None]:
                return False, f"Invalid interpretation area. Must be one of: {', '.join(valid_areas)}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating interpretation request: {str(e)}", exc_info=True)
            return False, str(e)

    def generate_interpretation(
        self,
        birth_chart: Optional[Dict] = None,
        date_of_birth: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        level: str = "basic",
        area: str = "general"
    ) -> Dict:
        """Generate a complete interpretation for a birth chart."""
        try:
            logger.info(f"Generating interpretation (level: {level}, area: {area})")
            
            # Validate request parameters
            request = {
                "birth_chart": birth_chart,
                "date_of_birth": date_of_birth,
                "latitude": latitude,
                "longitude": longitude,
                "level": level,
                "area": area
            }
            
            is_valid, error_message = self._validate_interpretation_request(request)
            if not is_valid:
                logger.warning(f"Invalid interpretation request: {error_message}")
                return {
                    "status": "error",
                    "message": error_message
                }
            
            # Calculate birth chart if not provided
            if birth_chart is None and all(x is not None for x in [date_of_birth, latitude, longitude]):
                logger.info(f"Calculating birth chart for date: {date_of_birth}, location: {latitude}, {longitude}")
                birth_chart = self._calculate_birth_chart(date_of_birth, latitude, longitude)
            
            # Validate birth chart data
            if not self._validate_birth_chart(birth_chart):
                logger.warning("Invalid birth chart data")
                return {
                    "status": "error",
                    "message": "Invalid birth chart data structure or content"
                }
            
            # Generate interpretations
            logger.debug("Generating planet interpretations")
            planet_interpretations = self._get_planet_interpretations(birth_chart, level)
            
            logger.debug("Generating house interpretations")
            house_interpretations = self._get_house_interpretations(birth_chart, level)
            
            logger.debug("Generating aspect interpretations")
            aspect_interpretations = self._get_aspect_interpretations(birth_chart, level)
            
            logger.debug("Analyzing patterns")
            patterns = self._analyze_patterns(birth_chart)
            
            logger.debug("Analyzing combinations")
            combinations = self._analyze_combinations(birth_chart)
            
            logger.debug("Analyzing house emphasis")
            house_emphasis = self._analyze_house_emphasis(birth_chart)
            
            logger.debug("Analyzing special configurations")
            special_configurations = self._analyze_special_configurations(birth_chart)
            
            logger.debug("Analyzing planetary dignities")
            planetary_dignities = self._get_all_planet_dignities(birth_chart)
            
            logger.info("Successfully generated all interpretations")
            
            return {
                "status": "success",
                "data": {
                    "planets": birth_chart.get("planets", {}),
                    "houses": birth_chart.get("houses", {}),
                    "aspects": birth_chart.get("aspects", []),
                    "interpretations": {
                        "planets": planet_interpretations,
                        "houses": house_interpretations,
                        "aspects": aspect_interpretations
                    },
                    "patterns": patterns,
                    "combinations": combinations,
                    "house_emphasis": house_emphasis,
                    "special_configurations": special_configurations,
                    "planetary_dignities": planetary_dignities
                }
            }
        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def _calculate_birth_chart(self, date_of_birth: str, latitude: float, longitude: float) -> dict:
        """Calculate the birth chart using BirthChartService."""
        return self.birth_chart_service.calculate_birth_chart(
            date_of_birth=date_of_birth,
            latitude=latitude,
            longitude=longitude
        )

    def _calculate_planetary_positions(self, date: flatlib.Date) -> dict:
        """Calculate positions of planets using flatlib."""
        # Get planetary positions
        sun = flatlib.calc.Sun(date)
        moon = flatlib.calc.Moon(date)
        mercury = flatlib.calc.Mercury(date)
        venus = flatlib.calc.Venus(date)
        mars = flatlib.calc.Mars(date)
        jupiter = flatlib.calc.Jupiter(date)
        saturn = flatlib.calc.Saturn(date)
        uranus = flatlib.calc.Uranus(date)
        neptune = flatlib.calc.Neptune(date)
        pluto = flatlib.calc.Pluto(date)
        
        # Convert positions to our format
        return {
            "Sun": self._convert_planet_position(sun),
            "Moon": self._convert_planet_position(moon),
            "Mercury": self._convert_planet_position(mercury),
            "Venus": self._convert_planet_position(venus),
            "Mars": self._convert_planet_position(mars),
            "Jupiter": self._convert_planet_position(jupiter),
            "Saturn": self._convert_planet_position(saturn),
            "Uranus": self._convert_planet_position(uranus),
            "Neptune": self._convert_planet_position(neptune),
            "Pluto": self._convert_planet_position(pluto)
        }

    def _calculate_house_cusps(self, date: flatlib.Date, geoloc: flatlib.GeoPos) -> dict:
        """Calculate house cusps using flatlib."""
        # Get house cusps using Placidus system
        houses = flatlib.calc.Houses(date, geoloc)
        
        # Convert house cusps to our format
        return {
            str(i): self._convert_house_cusp(houses[i])
            for i in range(1, 13)
        }

    def _convert_planet_position(self, planet: flatlib.Object) -> dict:
        """Convert flatlib planet position to our format."""
        return {
            "sign": self._get_sign_from_degree(planet.lon),
            "degree": planet.lon,
            "house": self._get_house_from_degree(planet.lon)
        }

    def _convert_house_cusp(self, cusp: flatlib.Object) -> dict:
        """Convert flatlib house cusp to our format."""
        return {
            "sign": self._get_sign_from_degree(cusp.lon),
            "degree": cusp.lon
        }

    def _get_sign_from_degree(self, degree: float) -> str:
        """Convert degree to zodiac sign."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_index = int(degree / 30)
        return signs[sign_index]

    def _get_house_from_degree(self, degree: float) -> int:
        """Convert degree to house number."""
        # This is a simplified version - actual house calculation depends on house system
        house = int(degree / 30) + 1
        return house if house <= 12 else 1

    def _calculate_aspects(self, planets: dict) -> List[dict]:
        """Calculate aspects between planets."""
        aspects = []
        planet_list = list(planets.keys())
        
        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                p1, p2 = planet_list[i], planet_list[j]
                if p1 == "Ascendant" or p2 == "Ascendant":
                    continue
                
                deg1 = planets[p1]["degree"]
                deg2 = planets[p2]["degree"]
                
                # Calculate angular distance
                angle = abs(deg1 - deg2)
                if angle > 180:
                    angle = 360 - angle
                
                # Check for major aspects
                if abs(angle - 0) <= 10:  # Conjunction
                    aspects.append({"planet1": p1, "planet2": p2, "type": 0})
                elif abs(angle - 60) <= 6:  # Sextile
                    aspects.append({"planet1": p1, "planet2": p2, "type": 60})
                elif abs(angle - 90) <= 8:  # Square
                    aspects.append({"planet1": p1, "planet2": p2, "type": 90})
                elif abs(angle - 120) <= 8:  # Trine
                    aspects.append({"planet1": p1, "planet2": p2, "type": 120})
                elif abs(angle - 180) <= 10:  # Opposition
                    aspects.append({"planet1": p1, "planet2": p2, "type": 180})
                elif abs(angle - 150) <= 3:  # Quincunx
                    aspects.append({"planet1": p1, "planet2": p2, "type": 150})
        
        return aspects

    def _calculate_planetary_dignities(self, planets: dict) -> dict:
        """Calculate planetary dignities based on positions."""
        dignities = {}
        for planet, data in planets.items():
            if planet == "Ascendant":
                continue
            sign = data.get("sign", "")
            if sign:
                dignities[planet] = self._get_planet_dignity(planet, sign)
        return dignities

    def _get_all_planet_dignities(self, birth_chart: dict) -> dict:
        """Get dignities for all planets in the birth chart."""
        dignities = {}
        for planet, data in birth_chart.get("planets", {}).items():
            sign = data.get("sign", "")
            if sign:
                dignities[planet.lower()] = self._get_planet_dignity(planet, sign)
        return dignities

    def _get_planet_interpretations(self, birth_chart: dict, level: str = "basic") -> dict:
        """Get interpretations for all planets in the birth chart."""
        interpretations = {}
        for planet, data in birth_chart.get("planets", {}).items():
            sign = data.get("sign", "")
            house = data.get("house")
            if sign:
                interpretations[planet.lower()] = self._get_planet_interpretation(planet, sign, level)
        return interpretations

    @lru_cache(maxsize=1000)
    def _get_planet_interpretation(self, planet: str, sign: str, level: str = "basic") -> str:
        """Get interpretation for a planet in a sign with caching."""
        planet = planet.lower()
        sign = sign.lower()
        
        if planet not in self._planet_cache or sign not in self._sign_cache:
            logger.warning(f"Invalid planet or sign: {planet}, {sign}")
            return ""
        
        planet_data = self._planet_cache[planet]
        sign_data = self._sign_cache[sign]
        
        interpretation = []
        interpretation.append(f"{planet.capitalize()} in {sign.capitalize()} represents {planet_data['qualities']}...")
        
        if level == "detailed":
            interpretation.append(f"Element: {sign_data['element'].name}")
            interpretation.append(f"Modality: {sign_data['modality'].name}")
            interpretation.append(f"Keywords: {', '.join(sign_data['keywords'])}")
            
            if planet in ['sun', 'moon']:
                interpretation.append(self._get_compatibility_interpretation(planet, sign))
        
        return " ".join(interpretation)

    @lru_cache(maxsize=1000)
    def _get_house_interpretation(self, house: str, sign: str, level: str = "basic") -> str:
        """Get interpretation for a house in a sign with caching."""
        house = str(house)
        sign = sign.lower()
        
        if house not in self._house_cache or sign not in self._sign_cache:
            logger.warning(f"Invalid house or sign: {house}, {sign}")
            return ""
        
        house_data = self._house_cache[house]
        sign_data = self._sign_cache[sign]
        
        interpretation = []
        interpretation.append(f"House {house} in {sign.capitalize()} represents {house_data['qualities']}...")
        
        if level == "detailed":
            interpretation.append(f"Element: {sign_data['element'].name}")
            interpretation.append(f"Modality: {sign_data['modality'].name}")
            interpretation.append(f"Keywords: {', '.join(sign_data['keywords'])}")
        
        return " ".join(interpretation)

    @lru_cache(maxsize=1000)
    def _get_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: str, orb: float = 0.0, level: str = "basic") -> str:
        """Get interpretation for an aspect between planets with caching."""
        planet1 = planet1.lower()
        planet2 = planet2.lower()
        aspect_type = aspect_type.lower()
        
        if (planet1 not in self._planet_cache or 
            planet2 not in self._planet_cache or 
            aspect_type not in self._aspect_cache):
            logger.warning(f"Invalid planet or aspect: {planet1}, {planet2}, {aspect_type}")
            return ""
        
        planet1_data = self._planet_cache[planet1]
        planet2_data = self._planet_cache[planet2]
        aspect_data = self._aspect_cache[aspect_type]
        
        interpretation = []
        interpretation.append(f"{planet1.capitalize()} {aspect_type} {planet2.capitalize()} indicates {aspect_data['nature']}...")
        
        if level == "detailed":
            interpretation.append(f"Type: {aspect_data['type']}")
            interpretation.append(f"Keywords: {', '.join(aspect_data['keywords'])}")
            if orb > 0:
                interpretation.append(f"Orb: {orb} degrees")
        
        return " ".join(interpretation)

    @lru_cache(maxsize=1000)
    def _get_element_modality_qualities(self, element: Element, modality: Modality) -> List[str]:
        """Get qualities for element-modality combination with caching."""
        qualities = []
        if element == Element.FIRE:
            if modality == Modality.CARDINAL:
                qualities.extend(["dynamic", "initiative", "leadership"])
            elif modality == Modality.FIXED:
                qualities.extend(["stability", "determination", "persistence"])
            else:  # MUTABLE
                qualities.extend(["adaptability", "versatility", "flexibility"])
        # Add similar logic for other elements
        return qualities

    @lru_cache(maxsize=1000)
    def _get_element_modality_keywords(self, element: Element, modality: Modality) -> List[str]:
        """Get keywords for element-modality combination with caching."""
        keywords = []
        if element == Element.FIRE:
            if modality == Modality.CARDINAL:
                keywords.extend(["action", "leadership", "initiative"])
            elif modality == Modality.FIXED:
                keywords.extend(["stability", "determination", "focus"])
            else:  # MUTABLE
                keywords.extend(["adaptability", "versatility", "change"])
        # Add similar logic for other elements
        return keywords

    def _analyze_patterns(self, birth_chart: dict) -> dict:
        """Analyze elemental and modality patterns in the birth chart."""
        logger.debug("Analyzing elemental and modality patterns")
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
        
        # Count elements and modalities
        for planet, data in birth_chart.get("planets", {}).items():
            sign = data.get("sign", "").lower()
            if sign in self.signs_data:
                sign_data = self.signs_data[sign]
                element = sign_data.get("element", "").lower()
                modality = sign_data.get("modality", "").lower()
                
                if element in elements:
                    elements[element] += 1
                if modality in modalities:
                    modalities[modality] += 1
        
        # Determine dominant elements and modalities
        dominant_elements = [e for e, c in elements.items() if c == max(elements.values())]
        dominant_modalities = [m for m, c in modalities.items() if c == max(modalities.values())]
        
        logger.debug(f"Dominant elements: {dominant_elements}, Dominant modalities: {dominant_modalities}")
        
        return {
            "counts": {
                "elements": elements,
                "modalities": modalities
            },
            "dominant": {
                "elements": dominant_elements,
                "modalities": dominant_modalities
            },
            "interpretation": f"The chart shows a balance between {' and '.join(dominant_elements)} elements..."
        }

    def _analyze_combinations(self, birth_chart: dict) -> dict:
        """Analyze significant planet combinations in the birth chart."""
        planets = birth_chart.get("planets", {})
        sun_sign = planets.get("Sun", {}).get("sign", "").lower()
        moon_sign = planets.get("Moon", {}).get("sign", "").lower()
        asc_sign = planets.get("Ascendant", {}).get("sign", "").lower()
        
        combinations = {
            "sun_moon": self._analyze_sun_moon_combination(sun_sign, moon_sign),
            "sun_rising": self._analyze_sun_rising_combination(sun_sign, asc_sign),
            "moon_rising": self._analyze_moon_rising_combination(moon_sign, asc_sign)
        }
        
        return combinations

    def _analyze_sun_moon_combination(self, sun_sign: str, moon_sign: str) -> dict:
        """Analyze the combination of Sun and Moon signs."""
        sun_sign = sun_sign.lower()
        moon_sign = moon_sign.lower()
        
        if sun_sign in self.signs_data and moon_sign in self.signs_data:
            sun_data = self.signs_data[sun_sign]
            moon_data = self.signs_data[moon_sign]
            
            interpretation = f"Sun in {sun_sign.capitalize()} with Moon in {moon_sign.capitalize()}\n"
            interpretation += f"This combination suggests a personality that blends {sun_data.get('qualities', {}).get('general', '')} "
            interpretation += f"with emotional needs characterized by {moon_data.get('qualities', {}).get('general', '')}"
            
            return {
                "interpretation": interpretation,
                "strength": self._calculate_combination_strength(sun_sign, moon_sign)
            }
        return {
            "interpretation": "",
            "strength": 0
        }

    def _analyze_sun_rising_combination(self, sun_sign: str, asc_sign: str) -> dict:
        """Analyze the combination of Sun and Ascendant signs."""
        sun_sign = sun_sign.lower()
        asc_sign = asc_sign.lower()
        
        if sun_sign in self.signs_data and asc_sign in self.signs_data:
            sun_data = self.signs_data[sun_sign]
            asc_data = self.signs_data[asc_sign]
            
            interpretation = f"Sun in {sun_sign.capitalize()} with {asc_sign.capitalize()} Ascending\n"
            interpretation += f"This combination suggests an outer personality that {asc_data.get('qualities', {}).get('general', '')} "
            interpretation += f"with an inner drive that {sun_data.get('qualities', {}).get('general', '')}"
            
            return {
                "interpretation": interpretation,
                "strength": self._calculate_combination_strength(sun_sign, asc_sign)
            }
        return {
            "interpretation": "",
            "strength": 0
        }

    def _analyze_moon_rising_combination(self, moon_sign: str, asc_sign: str) -> dict:
        """Analyze the combination of Moon and Ascendant signs."""
        moon_sign = moon_sign.lower()
        asc_sign = asc_sign.lower()
        
        if moon_sign in self.signs_data and asc_sign in self.signs_data:
            moon_data = self.signs_data[moon_sign]
            asc_data = self.signs_data[asc_sign]
            
            interpretation = f"Moon in {moon_sign.capitalize()} with {asc_sign.capitalize()} Ascending\n"
            interpretation += f"This combination suggests emotional needs that {moon_data.get('qualities', {}).get('general', '')} "
            interpretation += f"expressed through a personality that {asc_data.get('qualities', {}).get('general', '')}"
            
            return {
                "interpretation": interpretation,
                "strength": self._calculate_combination_strength(moon_sign, asc_sign)
            }
        return {
            "interpretation": "",
            "strength": 0
        }

    def _calculate_combination_strength(self, sign1: str, sign2: str) -> float:
        """Calculate the strength of a combination between two signs."""
        sign1 = sign1.lower()
        sign2 = sign2.lower()
        
        if sign1 not in self.signs_data or sign2 not in self.signs_data:
            return 0.0
        
        sign1_data = self.signs_data[sign1]
        sign2_data = self.signs_data[sign2]
        
        # Calculate strength based on element and modality compatibility
        element_strength = 0.5 if sign1_data.get("element") == sign2_data.get("element") else 0.0
        modality_strength = 0.5 if sign1_data.get("modality") == sign2_data.get("modality") else 0.0
        
        return element_strength + modality_strength

    def _analyze_house_emphasis(self, birth_chart: dict) -> dict:
        """Analyze the emphasis on different house types."""
        logger.debug("Analyzing house emphasis")
        houses = birth_chart.get("houses", {})
        planets = birth_chart.get("planets", {})
        
        # Count planets in each house type
        angular_count = 0
        succedent_count = 0
        cadent_count = 0
        
        for planet, data in planets.items():
            house = data.get("house")
            if house:
                if house in [1, 4, 7, 10]:
                    angular_count += 1
                elif house in [2, 5, 8, 11]:
                    succedent_count += 1
                elif house in [3, 6, 9, 12]:
                    cadent_count += 1
        
        counts = {
            "angular": angular_count,
            "succedent": succedent_count,
            "cadent": cadent_count
        }
        
        dominant = max(counts, key=counts.get)
        logger.debug(f"House emphasis: {dominant} ({counts[dominant]} planets)")
        
        return {
            "counts": counts,
            "dominant": dominant,
            "interpretation": f"Emphasis on {dominant} houses indicates {self._get_house_emphasis_interpretation(dominant)}"
        }

    def _get_house_emphasis_interpretation(self, emphasis: str) -> str:
        """Get interpretation for house emphasis."""
        interpretations = {
            "angular": "a focus on action, initiative, and personal expression",
            "succedent": "a focus on stability, resources, and values",
            "cadent": "a focus on learning, communication, and adaptability"
        }
        return interpretations.get(emphasis, "")

    def _analyze_special_configurations(self, birth_chart: dict) -> dict:
        """Analyze special planetary configurations."""
        logger.debug("Analyzing special configurations")
        aspects = birth_chart.get("aspects", [])
        planets = birth_chart.get("planets", {})
        
        configurations = {
            "grand_trine": self._find_grand_trine(aspects),
            "t_square": self._find_t_square(aspects),
            "grand_cross": self._find_grand_cross(aspects),
            "yod": self._find_yod(aspects),
            "stellium": self._find_stellium(planets)
        }
        
        # Log found configurations
        for config_type, config_list in configurations.items():
            if config_list:
                logger.debug(f"Found {len(config_list)} {config_type} configurations")
        
        return {
            "configurations": configurations,
            "interpretation": self._get_configuration_interpretation(configurations)
        }

    def _find_grand_trine(self, aspects: List[dict]) -> List[dict]:
        """Find grand trine configurations (three planets in trine aspect)."""
        trines = [a for a in aspects if a.get("type") == 120]
        grand_trines = []
        
        # Group trines by planet
        planet_trines = {}
        for trine in trines:
            p1, p2 = trine["planet1"], trine["planet2"]
            if p1 not in planet_trines:
                planet_trines[p1] = []
            if p2 not in planet_trines:
                planet_trines[p2] = []
            planet_trines[p1].append(p2)
            planet_trines[p2].append(p1)
        
        # Find cycles of three planets
        for planet, connected in planet_trines.items():
            for p2 in connected:
                for p3 in planet_trines.get(p2, []):
                    if p3 in planet_trines.get(planet, []):
                        # Found a grand trine
                        grand_trine = {
                            "planets": sorted([planet, p2, p3]),
                            "type": "grand_trine",
                            "aspects": [
                                {"planet1": planet, "planet2": p2, "type": 120},
                                {"planet1": p2, "planet2": p3, "type": 120},
                                {"planet1": p3, "planet2": planet, "type": 120}
                            ]
                        }
                        # Avoid duplicates
                        if grand_trine not in grand_trines:
                            grand_trines.append(grand_trine)
        
        return grand_trines

    def _find_t_square(self, aspects: List[dict]) -> List[dict]:
        """Find T-square configurations (two planets in opposition with a third planet square to both)."""
        squares = [a for a in aspects if a.get("type") == 90]
        oppositions = [a for a in aspects if a.get("type") == 180]
        t_squares = []
        
        # Group oppositions by planet
        planet_oppositions = {}
        for opp in oppositions:
            p1, p2 = opp["planet1"], opp["planet2"]
            if p1 not in planet_oppositions:
                planet_oppositions[p1] = []
            if p2 not in planet_oppositions:
                planet_oppositions[p2] = []
            planet_oppositions[p1].append(p2)
            planet_oppositions[p2].append(p1)
        
        # Find T-squares
        for planet, opposed in planet_oppositions.items():
            for p2 in opposed:
                # Look for a third planet square to both
                for square in squares:
                    p3 = square["planet1"] if square["planet2"] in [planet, p2] else square["planet2"]
                    if p3 not in [planet, p2]:
                        t_square = {
                            "planets": sorted([planet, p2, p3]),
                            "type": "t_square",
                            "apex": p3,  # The planet square to the opposition
                            "base": [planet, p2],  # The planets in opposition
                            "aspects": [
                                {"planet1": planet, "planet2": p2, "type": 180},
                                {"planet1": planet, "planet2": p3, "type": 90},
                                {"planet1": p2, "planet2": p3, "type": 90}
                            ]
                        }
                        # Avoid duplicates
                        if t_square not in t_squares:
                            t_squares.append(t_square)
        
        return t_squares

    def _find_grand_cross(self, aspects: List[dict]) -> List[dict]:
        """Find grand cross configurations (four planets forming two oppositions and four squares)."""
        squares = [a for a in aspects if a.get("type") == 90]
        oppositions = [a for a in aspects if a.get("type") == 180]
        grand_crosses = []
        
        # Group oppositions by planet
        planet_oppositions = {}
        for opp in oppositions:
            p1, p2 = opp["planet1"], opp["planet2"]
            if p1 not in planet_oppositions:
                planet_oppositions[p1] = []
            if p2 not in planet_oppositions:
                planet_oppositions[p2] = []
            planet_oppositions[p1].append(p2)
            planet_oppositions[p2].append(p1)
        
        # Find grand crosses
        for planet, opposed in planet_oppositions.items():
            for p2 in opposed:
                # Look for another opposition
                for p3, p4_opposed in planet_oppositions.items():
                    if p3 not in [planet, p2]:
                        for p4 in p4_opposed:
                            if p4 not in [planet, p2, p3]:
                                # Check if all squares exist
                                required_squares = [
                                    (planet, p3), (planet, p4),
                                    (p2, p3), (p2, p4)
                                ]
                                if all(self._has_aspect(squares, p1, p2, 90) for p1, p2 in required_squares):
                                    grand_cross = {
                                        "planets": sorted([planet, p2, p3, p4]),
                                        "type": "grand_cross",
                                        "aspects": [
                                            {"planet1": planet, "planet2": p2, "type": 180},
                                            {"planet1": p3, "planet2": p4, "type": 180},
                                            {"planet1": planet, "planet2": p3, "type": 90},
                                            {"planet1": planet, "planet2": p4, "type": 90},
                                            {"planet1": p2, "planet2": p3, "type": 90},
                                            {"planet1": p2, "planet2": p4, "type": 90}
                                        ]
                                    }
                                    # Avoid duplicates
                                    if grand_cross not in grand_crosses:
                                        grand_crosses.append(grand_cross)
        
        return grand_crosses

    def _find_yod(self, aspects: List[dict]) -> List[dict]:
        """Find yod configurations (two planets in sextile with both quincunx to a third planet)."""
        sextiles = [a for a in aspects if a.get("type") == 60]
        quincunxes = [a for a in aspects if a.get("type") == 150]
        yods = []
        
        # Group sextiles by planet
        planet_sextiles = {}
        for sextile in sextiles:
            p1, p2 = sextile["planet1"], sextile["planet2"]
            if p1 not in planet_sextiles:
                planet_sextiles[p1] = []
            if p2 not in planet_sextiles:
                planet_sextiles[p2] = []
            planet_sextiles[p1].append(p2)
            planet_sextiles[p2].append(p1)
        
        # Find yods
        for planet, sextiled in planet_sextiles.items():
            for p2 in sextiled:
                # Look for a third planet quincunx to both
                for quincunx in quincunxes:
                    p3 = quincunx["planet1"] if quincunx["planet2"] in [planet, p2] else quincunx["planet2"]
                    if p3 not in [planet, p2]:
                        # Check if p3 is quincunx to both p1 and p2
                        if (self._has_aspect(quincunxes, planet, p3, 150) and 
                            self._has_aspect(quincunxes, p2, p3, 150)):
                            yod = {
                                "planets": sorted([planet, p2, p3]),
                                "type": "yod",
                                "apex": p3,  # The planet quincunx to both
                                "base": [planet, p2],  # The planets in sextile
                                "aspects": [
                                    {"planet1": planet, "planet2": p2, "type": 60},
                                    {"planet1": planet, "planet2": p3, "type": 150},
                                    {"planet1": p2, "planet2": p3, "type": 150}
                                ]
                            }
                            # Avoid duplicates
                            if yod not in yods:
                                yods.append(yod)
        
        return yods

    def _has_aspect(self, aspects: List[dict], planet1: str, planet2: str, aspect_type: int) -> bool:
        """Helper method to check if an aspect exists between two planets."""
        return any(
            (a["planet1"] == planet1 and a["planet2"] == planet2 and a["type"] == aspect_type) or
            (a["planet1"] == planet2 and a["planet2"] == planet1 and a["type"] == aspect_type)
            for a in aspects
        )

    def _find_stellium(self, planets: dict) -> List[dict]:
        """Find stellium configurations (3+ planets in same sign)."""
        stelliums = []
        
        # Group planets by sign
        sign_planets = {}
        for planet, data in planets.items():
            sign = data.get("sign")
            if sign:
                if sign not in sign_planets:
                    sign_planets[sign] = []
                sign_planets[sign].append(planet)
        
        # Find signs with 3 or more planets
        for sign, planet_list in sign_planets.items():
            if len(planet_list) >= 3:
                stellium = {
                    "sign": sign,
                    "planets": sorted(planet_list),
                    "count": len(planet_list),
                    "type": "stellium"
                }
                stelliums.append(stellium)
        
        return stelliums

    def _get_configuration_interpretation(self, configurations: dict) -> str:
        """Get interpretation for special configurations."""
        interpretations = []
        
        for config_type, config_list in configurations.items():
            if config_list:
                template = self.pattern_interpretations.get("configurations", {}).get(config_type, "")
                if template:
                    for config in config_list:
                        planets = config.get("planets", [])
                        planet_names = ", ".join(planets)
                        
                        # Add specific details based on configuration type
                        if config_type == "t_square":
                            apex = config.get("apex", "")
                            base = config.get("base", [])
                            if apex and base:
                                detail = f" involving {apex} as the apex planet and {', '.join(base)} as the base planets"
                            else:
                                detail = f" involving {planet_names}"
                        elif config_type == "yod":
                            apex = config.get("apex", "")
                            base = config.get("base", [])
                            if apex and base:
                                detail = f" with {apex} as the apex planet and {', '.join(base)} as the base planets"
                            else:
                                detail = f" involving {planet_names}"
                        elif config_type == "stellium":
                            sign = config.get("sign", "")
                            if sign:
                                detail = f" in {sign.capitalize()} sign"
                            else:
                                detail = f" involving {planet_names}"
                        else:
                            detail = f" involving {planet_names}"
                        
                        interpretations.append(f"{config_type.replace('_', ' ').title()}{detail}: {template}")
        
        if not interpretations:
            return "No major configurations found."
        
        # Group interpretations by type for better readability
        grouped = {}
        for interpretation in interpretations:
            config_type = interpretation.split(":")[0].strip()
            if config_type not in grouped:
                grouped[config_type] = []
            grouped[config_type].append(interpretation)
        
        # Format the final output
        final_interpretations = []
        for config_type, config_interpretations in grouped.items():
            if len(config_interpretations) > 1:
                final_interpretations.append(f"{config_type}:")
                for interpretation in config_interpretations:
                    final_interpretations.append(f"  - {interpretation.split(':')[1].strip()}")
            else:
                final_interpretations.append(interpretation)
        
        return "\n".join(final_interpretations)

    # Alias methods for test compatibility
    def _get_sun_moon_combination_interpretation(self, sun_sign: str, moon_sign: str) -> str:
        """Get interpretation for Sun-Moon combination."""
        sun_sign = sun_sign.lower()
        moon_sign = moon_sign.lower()
        
        if sun_sign in self.signs_data and moon_sign in self.signs_data:
            sun_data = self.signs_data[sun_sign]
            moon_data = self.signs_data[moon_sign]
            
            interpretation = f"Sun in {sun_sign.capitalize()} - Moon in {moon_sign.capitalize()}\n"
            interpretation += f"Sun qualities: {sun_data.get('qualities', {}).get('general', '')}\n"
            interpretation += f"Moon qualities: {moon_data.get('qualities', {}).get('general', '')}"
            
            return interpretation
        return ""

    def _get_sun_rising_combination_interpretation(self, sun_sign: str, rising_sign: str) -> str:
        """Get interpretation for Sun-Rising combination."""
        sun_sign = sun_sign.lower()
        rising_sign = rising_sign.lower()
        
        if sun_sign in self.signs_data and rising_sign in self.signs_data:
            sun_data = self.signs_data[sun_sign]
            rising_data = self.signs_data[rising_sign]
            
            interpretation = f"Sun in {sun_sign.capitalize()} - Rising in {rising_sign.capitalize()}\n"
            interpretation += f"Sun qualities: {sun_data.get('qualities', {}).get('general', '')}\n"
            interpretation += f"Rising qualities: {rising_data.get('qualities', {}).get('general', '')}"
            
            return interpretation
        return ""

    def _get_moon_rising_combination_interpretation(self, moon_sign: str, rising_sign: str) -> str:
        """Get interpretation for Moon-Rising combination."""
        moon_sign = moon_sign.lower()
        rising_sign = rising_sign.lower()
        
        if moon_sign in self.signs_data and rising_sign in self.signs_data:
            moon_data = self.signs_data[moon_sign]
            rising_data = self.signs_data[rising_sign]
            
            interpretation = f"Moon in {moon_sign.capitalize()} - Rising in {rising_sign.capitalize()}\n"
            interpretation += f"Moon qualities: {moon_data.get('qualities', {}).get('general', '')}\n"
            interpretation += f"Rising qualities: {rising_data.get('qualities', {}).get('general', '')}"
            
            return interpretation
        return ""

    @lru_cache(maxsize=1000)
    def _get_planet_dignity(self, planet: str, sign: str) -> str:
        """Get planet dignity in a sign with caching."""
        if planet not in self._planet_cache or sign not in self._sign_cache:
            return "neutral"
        
        planet_data = self._planet_cache[planet]
        sign_data = self._sign_cache[sign]
        
        # Check for dignity based on planet's dignities and sign
        for dignity, signs in planet_data['dignities'].items():
            if sign in [s.name.lower() for s in signs]:
                return dignity.name.lower()
        
        return "neutral"

    def _get_compatibility_interpretation(self, planet: str, sign: str) -> str:
        """Get compatibility interpretation for a planet in a sign."""
        planet = planet.lower()
        sign = sign.lower()
        
        if planet in self.signs_data and sign in self.signs_data:
            planet_data = self.signs_data[planet]
            sign_data = self.signs_data[sign]
            
            compatibility = []
            for aspect in ["career", "relationships", "health", "spirituality", "personal_growth"]:
                planet_quality = planet_data.get("qualities", {}).get(aspect, "")
                sign_quality = sign_data.get("qualities", {}).get(aspect, "")
                if planet_quality or sign_quality:
                    compatibility.append(f"{aspect.capitalize()}: {planet_quality}; {sign_quality}")
            
            if planet in ["sun", "moon"] and sign_data.get("compatible_signs"):
                compatible_signs = ", ".join(sign_data["compatible_signs"])
                compatibility.append(f"Compatible with: {compatible_signs}")
            
            return "\n".join(compatibility)
        return "" 