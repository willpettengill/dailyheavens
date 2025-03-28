from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, List, Optional, Union
import flatlib
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import os
import copy
import csv

from app.core.config import settings
from app.models.interpretation import InterpretationRequest, InterpretationResponse
import logging
from functools import lru_cache
from app.models.astrology import (
    Planet, House, Aspect, AspectType,
    Element, Modality, Dignity, HouseType
)
from app.services.birth_chart import BirthChartService
from app.services.chart_statistics import ChartStatisticsService

logger = logging.getLogger(__name__)

class InterpretationService:
    def __init__(self):
        """Initialize the interpretation service."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing InterpretationService")
        
        # Set up data directory
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "structured"
        
        # Initialize caches
        self._planet_cache = {}
        self._house_cache = {}
        self._aspect_cache = {}
        self._pattern_cache = {}
        self._combination_cache = {}
        self._element_modality_cache = {}
        self._sign_cache = {}
        
        # Load structured data
        self.logger.info("Loading structured data files")
        self._load_structured_data()
        self.logger.info("Successfully loaded all structured data files")
        
        # Initialize other attributes
        self.birth_chart_service = BirthChartService()
        
        # Initialize statistics service
        try:
            self.statistics_service = ChartStatisticsService()
            self.logger.info("Chart statistics service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize statistics service: {str(e)}")
            self.statistics_service = None
        
        self.logger.info("InterpretationService initialized successfully")
        
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

    def _load_structured_data(self):
        """Load all structured data from JSON files."""
        try:
            # Load planets data
            with open(self.data_dir / "planets.json", 'r') as f:
                planets_data = json.load(f)
                self._planet_cache = {k.lower(): v for k, v in planets_data.items()}
            
            # Load signs data
            with open(self.data_dir / "signs.json", 'r') as f:
                signs_data = json.load(f)
                self._sign_cache = {k.lower(): v for k, v in signs_data.items()}
            
            # Load houses data
            with open(self.data_dir / "houses.json", 'r') as f:
                houses_data = json.load(f)
                self._house_cache = {k.lower(): v for k, v in houses_data.items()}
            
            # Load aspects data
            with open(self.data_dir / "aspects.json", 'r') as f:
                aspects_data = json.load(f)
                self._aspect_cache = {k.lower(): v for k, v in aspects_data.items()}
            
            # Load interpretation patterns
            with open(self.data_dir / "interpretation_patterns.json", 'r') as f:
                patterns_data = json.load(f)
                self._pattern_cache = patterns_data
            
            # Load combinations data
            with open(self.data_dir / "combinations.json", 'r') as f:
                combinations_data = json.load(f)
                self._combination_cache = combinations_data
            
            # Add numeric representations of aspects
            aspect_numeric = {
                "0": "conjunction",
                "60": "sextile", 
                "90": "square",
                "120": "trine",
                "180": "opposition"
            }
            
            # Update aspect cache with numeric keys
            for num, aspect in aspect_numeric.items():
                if aspect in self._aspect_cache:
                    self._aspect_cache[num] = self._aspect_cache[aspect]
            
            self.logger.info("Successfully loaded all structured data files")
            
        except Exception as e:
            self.logger.error(f"Error loading structured data: {str(e)}", exc_info=True)
            raise

    def _initialize_caches(self):
        """Initialize all caches with pre-computed data."""
        # Cache sign data using the signs_data dictionary
        self._sign_cache = {
            sign.lower(): data for sign, data in self.signs_data.items()
        }
        
        # Cache planet data using the planets_data dictionary
        self._planet_cache = {
            planet.lower(): data for planet, data in self.planets_data.items()
        }
        
        # Add common variations of planet names and ensure all are lowercase
        planet_variations = {
            "sun": ["sun", "sol"],
            "moon": ["moon", "luna"],
            "mercury": ["mercury"],
            "venus": ["venus"],
            "mars": ["mars"],
            "jupiter": ["jupiter"],
            "saturn": ["saturn"],
            "uranus": ["uranus"],
            "neptune": ["neptune"],
            "pluto": ["pluto"],
            "ascendant": ["ascendant", "asc"],
            "midheaven": ["midheaven", "mc"]
        }
        
        # Update planet cache with all variations
        for primary_planet, variations in planet_variations.items():
            if primary_planet.lower() in self._planet_cache:
                planet_data = self._planet_cache[primary_planet.lower()]
                for variation in variations:
                    self._planet_cache[variation.lower()] = planet_data
        
        # Cache aspect data using the aspects_data dictionary
        self._aspect_cache = {
            aspect.lower(): data for aspect, data in self.aspects_data.items()
            }
        
        # Add numeric representations of aspects
        aspect_numeric = {
            "0": "conjunction",
            "60": "sextile", 
            "90": "square",
            "120": "trine",
            "180": "opposition"
        }
        
        # Update aspect cache with numeric keys
        for num, aspect in aspect_numeric.items():
            if aspect in self._aspect_cache:
                self._aspect_cache[num] = self._aspect_cache[aspect]
        
        # Cache house data
        self._house_cache = {}
        for house_num in range(1, 13):
            house_data = self.houses_data.get(str(house_num), {})
            self._house_cache[str(house_num)] = {
                'type': house_data.get('type', ''),
                'qualities': house_data.get('qualities', {}),
                'keywords': house_data.get('keywords', [])
            }
        
        # Pre-compute element-modality combinations
        self._element_modality_cache = {}
        elements = ["fire", "earth", "air", "water"]
        modalities = ["cardinal", "fixed", "mutable"]
        
        for element in elements:
            for modality in modalities:
                key = f"{element}_{modality}"
                self._element_modality_cache[key] = {
                    'qualities': self._get_element_modality_qualities_simple(element, modality),
                    'keywords': self._get_element_modality_keywords_simple(element, modality)
                }
    
    def _get_element_modality_qualities_simple(self, element: str, modality: str) -> List[str]:
        """Get qualities for element-modality combination without using enums."""
        qualities = []
        if element == "fire":
            if modality == "cardinal":
                qualities.extend(["dynamic", "initiative", "leadership"])
            elif modality == "fixed":
                qualities.extend(["stability", "determination", "persistence"])
            else:  # mutable
                qualities.extend(["adaptability", "versatility", "flexibility"])
        elif element == "earth":
            if modality == "cardinal":
                qualities.extend(["practical", "ambitious", "disciplined"])
            elif modality == "fixed":
                qualities.extend(["reliable", "patient", "persistent"])
            else:  # mutable
                qualities.extend(["analytical", "discriminating", "helpful"])
        elif element == "air":
            if modality == "cardinal":
                qualities.extend(["intellectual", "objective", "social"])
            elif modality == "fixed":
                qualities.extend(["idealistic", "humanitarian", "detached"])
            else:  # mutable
                qualities.extend(["communicative", "curious", "versatile"])
        elif element == "water":
            if modality == "cardinal":
                qualities.extend(["emotional", "nurturing", "protective"])
            elif modality == "fixed":
                qualities.extend(["intense", "passionate", "deep"])
            else:  # mutable
                qualities.extend(["intuitive", "empathetic", "responsive"])
        return qualities
    
    def _get_element_modality_keywords_simple(self, element: str, modality: str) -> List[str]:
        """Get keywords for element-modality combination without using enums."""
        keywords = []
        if element == "fire":
            if modality == "cardinal":
                keywords.extend(["action", "leadership", "initiative"])
            elif modality == "fixed":
                keywords.extend(["stability", "determination", "focus"])
            else:  # mutable
                keywords.extend(["adaptability", "versatility", "change"])
        elif element == "earth":
            if modality == "cardinal":
                keywords.extend(["structure", "achievement", "planning"])
            elif modality == "fixed":
                keywords.extend(["security", "endurance", "resources"])
            else:  # mutable
                keywords.extend(["service", "organization", "improvement"])
        elif element == "air":
            if modality == "cardinal":
                keywords.extend(["ideas", "balance", "justice"])
            elif modality == "fixed":
                keywords.extend(["innovation", "friendship", "teamwork"])
            else:  # mutable
                keywords.extend(["logic", "information", "exchange"])
        elif element == "water":
            if modality == "cardinal":
                keywords.extend(["nurturing", "security", "care"])
            elif modality == "fixed":
                keywords.extend(["transformation", "depth", "investigation"])
            else:  # mutable
                keywords.extend(["healing", "compassion", "transcendence"])
        return keywords

    def _validate_birth_chart(self, birth_chart: Dict[str, Any]) -> bool:
        """Validate the birth chart data structure."""
        if not isinstance(birth_chart, dict):
            return False
            
        required_keys = ["planets", "houses", "aspects"]
        if not all(key in birth_chart for key in required_keys):
            return False
        
        # Validate planets
        if not isinstance(birth_chart["planets"], dict):
            return False
        
        for planet, data in birth_chart["planets"].items():
            if not isinstance(data, dict):
                return False
            required_planet_keys = ["sign", "degree", "house", "retrograde"]
            if not all(key in data for key in required_planet_keys):
                return False
            if not isinstance(data["sign"], str):
                return False
            if not isinstance(data["degree"], (int, float)):
                return False
            if not isinstance(data["house"], int):
                return False
            if not isinstance(data["retrograde"], bool):
                return False
        
        # Validate houses
        if not isinstance(birth_chart["houses"], dict):
            return False
        
        for house_num, data in birth_chart["houses"].items():
            if not isinstance(data, dict):
                return False
            required_house_keys = ["sign", "degree"]
            if not all(key in data for key in required_house_keys):
                return False
            if not isinstance(data["sign"], str):
                return False
            if not isinstance(data["degree"], (int, float)):
                return False
        
        # Validate aspects
        if not isinstance(birth_chart["aspects"], list):
            return False
        
        for aspect in birth_chart["aspects"]:
            if not isinstance(aspect, dict):
                return False
            required_aspect_keys = ["planet1", "planet2", "type", "orb"]
            if not all(key in aspect for key in required_aspect_keys):
                return False
            if not isinstance(aspect["planet1"], str):
                return False
            if not isinstance(aspect["planet2"], str):
                return False
            if not isinstance(aspect["type"], str):
                return False
            if not isinstance(aspect["orb"], (int, float)):
                return False
        
        return True

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

    def generate_interpretation(self, birth_chart: Dict[str, Any], level: str = "basic", area: str = "general") -> Dict[str, Any]:
        """Generate a complete interpretation of the birth chart.
        
        Args:
            birth_chart: Dictionary containing birth chart data
            level: Level of detail for the interpretation
            area: Area of life to focus on
            
        Returns:
            Dictionary containing the interpretation results
        """
        self.logger.info(f"Generating interpretation (level: {level}, area: {area})")
        
        try:
            # Validate birth chart data
            if not birth_chart or "planets" not in birth_chart:
                self.logger.warning("Invalid birth chart data")
                return {"status": "error", "message": "Invalid birth chart data"}
                
            # Create a simplified interpretation
            interpretations = {
                "planets": [],
                "houses": [],
                "aspects": [],
                "patterns": [],
                "combinations": {}
            }
            
            # Generate enhanced planet interpretations
            for planet_name, planet_data in birth_chart.get("planets", {}).items():
                try:
                    sign = planet_data.get("sign", "")
                    house = planet_data.get("house")
                    retrograde = planet_data.get("retrograde", False)
                    
                    if sign and house is not None:
                        # Get planet qualities based on area of focus
                        planet_quality = ""
                        normalized_planet = planet_name.lower()
                        if normalized_planet in self._planet_cache:
                            qualities = self._planet_cache[normalized_planet].get("qualities", {})
                            planet_quality = qualities.get(area, qualities.get("general", ""))
                        
                        # Get sign qualities
                        sign_quality = ""
                        normalized_sign = sign.lower()
                        if normalized_sign in self._sign_cache:
                            qualities = self._sign_cache[normalized_sign].get("qualities", {})
                            sign_quality = qualities.get(area, qualities.get("general", ""))
                        
                        # Get house meaning
                        house_meaning = ""
                        if str(house) in self._house_cache:
                            house_data = self._house_cache[str(house)]
                            house_meaning = house_data.get("qualities", {}).get(area, house_data.get("qualities", {}).get("general", ""))
                        
                        # Create interpretation
                        base_interpretation = f"{planet_name} in {sign} (House {house})"
                        if retrograde:
                            base_interpretation += " Retrograde"
                        
                        # Add qualities to interpretation
                        if planet_quality:
                            base_interpretation += f" - {planet_quality}"
                        if sign_quality:
                            base_interpretation += f" - {sign_quality}"
                        if house_meaning:
                            base_interpretation += f" - {house_meaning}"
                        
                        interpretations["planets"].append({
                            "planet": planet_name,
                            "sign": sign,
                            "house": house,
                            "retrograde": retrograde,
                            "interpretation": base_interpretation
                        })
                except Exception as e:
                    self.logger.error(f"Error generating planet interpretation: {str(e)}")
                    continue
            
            # Generate house interpretations
            for house_num, house_data in birth_chart.get("houses", {}).items():
                try:
                    sign = house_data.get("sign", "")
                    if sign and house_num in self._house_cache:
                        house_info = self._house_cache[house_num]
                        sign_info = self._sign_cache.get(sign.lower(), {})
                        
                        # Get house qualities
                        house_qualities = house_info.get("qualities", {}).get(area, house_info.get("qualities", {}).get("general", ""))
                        
                        # Get sign qualities
                        sign_qualities = sign_info.get("qualities", {}).get(area, sign_info.get("qualities", {}).get("general", ""))
                        
                        # Create interpretation
                        interpretation = f"House {house_num} in {sign}"
                        if house_qualities:
                            interpretation += f" - {house_qualities}"
                        if sign_qualities:
                            interpretation += f" - {sign_qualities}"
                        
                        interpretations["houses"].append({
                            "house": house_num,
                            "sign": sign,
                            "interpretation": interpretation
                        })
                except Exception as e:
                    self.logger.error(f"Error generating house interpretation: {str(e)}")
                    continue
            
            # Generate aspect interpretations
            for aspect in birth_chart.get("aspects", []):
                try:
                    planet1 = aspect.get("planet1", "")
                    planet2 = aspect.get("planet2", "")
                    aspect_type = aspect.get("type", "")
                    
                    if planet1 and planet2 and aspect_type:
                        # Get aspect information
                        aspect_info = self._aspect_cache.get(aspect_type.lower(), {})
                        
                        # Create interpretation
                        interpretation = f"{planet1} {aspect_type} {planet2}"
                        if aspect_info:
                            interpretation += f" - {aspect_info.get('description', '')}"
                        
                        interpretations["aspects"].append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "type": aspect_type,
                            "interpretation": interpretation
                        })
                except Exception as e:
                    self.logger.error(f"Error generating aspect interpretation: {str(e)}")
                    continue
            
            # Add patterns if detailed level
            if level == "detailed":
                try:
                    patterns = self._analyze_simple_patterns(birth_chart)
                    interpretations["patterns"] = patterns
                except Exception as e:
                    self.logger.error(f"Error analyzing patterns: {str(e)}")
            
            return {
                "status": "success",
                "data": {
                    "birth_chart": birth_chart,
                    "interpretations": interpretations
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating interpretation: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def _calculate_planetary_positions(self, date: Datetime) -> dict:
        """Calculate positions of planets using flatlib."""
        # This method should not be used anymore
        logger.warning("_calculate_planetary_positions was called but should not be used")
        return {}

    def _calculate_house_cusps(self, date: Datetime, latitude: float, longitude: float) -> dict:
        """Calculate house cusps."""
        # This method should not be used anymore
        logger.warning("_calculate_house_cusps was called but should not be used")
        return {}

    def _convert_planet_position(self, planet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert planet position data from the birth chart service."""
        return planet_data  # Already in the correct format

    def _convert_house_cusp(self, house_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert house cusp data from the birth chart service."""
        return house_data  # Already in the correct format

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
            if planet == "Ascendant" or planet == "Midheaven":
                continue
            sign = data.get("sign", "")
            house = data.get("house")
            if sign and house is not None:
                dignities[planet] = self._get_planet_dignity(planet, sign, house)
        return dignities

    def _get_planet_interpretations(self, birth_chart: dict, level: str = "basic") -> dict:
        """Get interpretations for all planets in the birth chart."""
        interpretations = {}
        for planet, data in birth_chart.get("planets", {}).items():
            sign = data.get("sign", "")
            if sign:
                planet_key = str(planet).lower() if planet is not None else ""
                interpretations[planet_key] = self._get_planet_interpretation(planet, sign, level)
        return interpretations

    def _normalize_planet_name(self, planet: str) -> str:
        """Normalize planet name to lowercase."""
        return planet.lower() if planet else ""

    def _normalize_sign_name(self, sign: str) -> str:
        """Normalize sign name to lowercase."""
        return sign.lower() if sign else ""

    def _validate_planet(self, planet: str) -> bool:
        """Validate if a planet exists in the data."""
        if not planet:
            return False
        normalized_planet = self._normalize_planet_name(planet)
        # Special handling for angles
        if normalized_planet in ["ascendant", "midheaven"]:
            return True
        return normalized_planet in self._planet_cache

    def _validate_sign(self, sign: str) -> bool:
        """Validate if a zodiac sign exists in the data."""
        if not sign:
            return False
        normalized_sign = self._normalize_sign_name(sign)
        return normalized_sign in self._sign_cache

    def _validate_planet_sign(self, planet: str, sign: str) -> bool:
        """Validate planet and sign combination."""
        normalized_planet = self._normalize_planet_name(planet)
        normalized_sign = self._normalize_sign_name(sign)
        
        if normalized_planet not in self.planets_data:
            logger.warning(f"Invalid planet: {planet}")
            return False
            
        if normalized_sign not in self.signs_data:
            logger.warning(f"Invalid sign: {sign}")
            return False
            
        return True

    def _validate_house_sign(self, house: int, sign: str) -> bool:
        """Validate house and sign combination."""
        normalized_sign = self._normalize_sign_name(sign)
        
        if str(house) not in self.houses_data:
            logger.warning(f"Invalid house: {house}")
            return False
            
        if normalized_sign not in self.signs_data:
            logger.warning(f"Invalid sign: {sign}")
            return False
            
        return True

    def _get_planet_interpretation(self, planet: str, sign: str, house: str, level: str = "basic") -> str:
        """Get interpretation for a planet in a sign and house.
        
        Args:
            planet: Planet name
            sign: Zodiac sign
            house: House number (as string)
            level: Level of detail
            
        Returns:
            Interpretation string
        """
        try:
            # Normalize inputs
            normalized_planet = self._normalize_planet_name(planet)
            normalized_sign = self._normalize_sign_name(sign)
            
            # Debug logging
            self.logger.debug(f"Getting interpretation for {normalized_planet} in {normalized_sign} (house {house})")
            self.logger.debug(f"Planet is in cache: {normalized_planet in self._planet_cache}")
            
            if normalized_planet not in self._planet_cache and normalized_planet not in ["ascendant", "midheaven"]:
                self.logger.warning(f"Planet not found in cache: {normalized_planet}")
                return f"No interpretation available for {planet}"
                
            if normalized_sign not in self._sign_cache:
                self.logger.warning(f"Sign not found in cache: {normalized_sign}")
                return f"No interpretation available for {planet} in {sign}"
            
            # Format planet name for display
            display_planet = planet.title() if planet else ""
            display_sign = sign.title() if sign else ""
            
            # Get planet qualities
            planet_qualities = self._planet_cache.get(normalized_planet, {}).get("qualities", {})
            planet_general = planet_qualities.get("general", "")
            
            # Get sign qualities
            sign_qualities = self._sign_cache.get(normalized_sign, {}).get("qualities", {})
            sign_general = sign_qualities.get("general", "")
            
            # Basic interpretation
            basic_interpretation = f"{display_planet} in {display_sign}: Your {planet_general} expresses through {sign_general}."
            
            # Return based on level
            if level == "basic":
                return basic_interpretation
            else:
                # Get house context
                house_num = str(house) if house else ""
                house_context = ""
                
                if house_num and house_num in self._house_cache:
                    house_type = self._house_cache[house_num].get("type", "")
                    house_qualities = self._house_cache[house_num].get("qualities", {}).get("general", "")
                    house_context = f" This manifests in the {house_num}th house of {house_qualities}."
                
                # Add house context to basic interpretation
                detailed_interpretation = basic_interpretation + house_context
                
                # Add more details for detailed interpretation
                if level == "detailed":
                    compatibility = self._get_compatibility_interpretation(normalized_planet, normalized_sign)
                    if compatibility:
                        detailed_interpretation += f" {compatibility}"
                
                return detailed_interpretation
        except Exception as e:
            self.logger.error(f"Error in _get_planet_interpretation: {str(e)}", exc_info=True)
            return f"Interpretation unavailable for {planet} in {sign} (House {house})"

    def _get_house_interpretation(self, house: str, sign: str, level: str = "basic") -> str:
        """Get interpretation for a house in a sign."""
        try:
            # Convert to lowercase for validation
            sign_lower = sign.lower()
            
            # Validate sign
            if not self._validate_sign(sign_lower):
                self.logger.warning(f"Invalid sign: {sign}")
                return f"Invalid sign: {sign}"
            
            # Get house and sign data (case-insensitive lookup)
            house_data = self.houses_data.get(house)
            if not house_data:
                self.logger.warning(f"Invalid house: {house}")
                return f"Invalid house: {house}"
            
            sign_data = next(v for k, v in self.signs_data.items() if k.lower() == sign_lower)
            
            # Build interpretation parts
            parts = []
            
            # Basic position
            parts.append(f"House {house} in {sign.title()}")
            
            # Keywords
            if "keywords" in house_data:
                parts.append(f"Keywords: {', '.join(house_data['keywords'])}")
            
            # Qualities
            if "qualities" in house_data:
                qualities = house_data["qualities"]
                if "general" in qualities:
                    parts.append(f"General: {qualities['general']}")
                if "career" in qualities:
                    parts.append(f"Career: {qualities['career']}")
                if "relationships" in qualities:
                    parts.append(f"Relationships: {qualities['relationships']}")
            
            # Sign information
            if "element" in sign_data:
                parts.append(f"Element: {sign_data['element'].title()}")
            if "modality" in sign_data:
                parts.append(f"Modality: {sign_data['modality'].title()}")
            
            # Sign qualities
            if "qualities" in sign_data:
                sign_qualities = sign_data["qualities"]
                if "general" in sign_qualities:
                    parts.append(f"Sign qualities: {sign_qualities['general']}")
            
            # Additional details for intermediate and advanced levels
            if level in ["intermediate", "advanced"]:
                if "qualities" in house_data:
                    qualities = house_data["qualities"]
                    if "health" in qualities:
                        parts.append(f"Health: {qualities['health']}")
                    if "spirituality" in qualities:
                        parts.append(f"Spirituality: {qualities['spirituality']}")
                    if "personal_growth" in qualities:
                        parts.append(f"Personal Growth: {qualities['personal_growth']}")
            
            return ". ".join(parts)
            
        except Exception as e:
            self.logger.error(f"Error generating house interpretation: {str(e)}")
            return f"Error generating house interpretation: {str(e)}"

    def _get_house_interpretations(self, birth_chart: Dict[str, Any], level: str = "basic") -> List[str]:
        """Get interpretations for all houses in the birth chart."""
        interpretations = []
        
        if "houses" not in birth_chart:
            logger.warning("No houses found in birth chart")
            return interpretations
            
        for house_num in range(1, 13):
            house_str = str(house_num)
            if house_str in birth_chart["houses"]:
                house_data = birth_chart["houses"][house_str]
                if "sign" in house_data:
                    interpretation = self._get_house_interpretation(
                        house_num,
                        house_data["sign"],
                        level
                    )
                    if interpretation:
                        interpretations.append(interpretation)
                        
        return interpretations

    def _find_grand_trine(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Grand Trine patterns in the aspects.
        
        Args:
            aspects: List of aspects in the birth chart
            
        Returns:
            List of dictionaries containing Grand Trine pattern information
        """
        grand_trines = []
        seen_combinations = set()
        
        # Group aspects by type
        trines = [a for a in aspects if str(a["type"]) == "120"]
        
        # Check each trine for potential Grand Trine
        for i, trine1 in enumerate(trines):
            planet1 = trine1["planet1"].lower()
            planet2 = trine1["planet2"].lower()
            
            # Look for trines to both planets
            for j, trine2 in enumerate(trines):
                if i != j:
                    trine2_p1 = trine2["planet1"].lower()
                    trine2_p2 = trine2["planet2"].lower()
                    if trine2_p1 in [planet1, planet2] or trine2_p2 in [planet1, planet2]:
                        for k, trine3 in enumerate(trines):
                            if k != i and k != j:
                                trine3_p1 = trine3["planet1"].lower()
                                trine3_p2 = trine3["planet2"].lower()
                                
                                # Check if this completes the Grand Trine
                                planets = {planet1, planet2}
                                planets.add(trine2_p1 if trine2_p1 not in planets else trine2_p2)
                                planets.add(trine3_p1 if trine3_p1 not in planets else trine3_p2)
                                
                                if len(planets) == 3:
                                    # Create a unique key for this combination
                                    key = "-".join(sorted(planets))
                                    if key not in seen_combinations:
                                        seen_combinations.add(key)
                                        planets_list = list(planets)
                                        # Get the element of the grand trine
                                        element = self._get_trine_element(planets_list)
                                        grand_trines.append({
                                            "planet1": planets_list[0],
                                            "planet2": planets_list[1],
                                            "planet3": planets_list[2],
                                            "planets": planets_list,
                                            "element": element if element else "unknown"
                                        })
        
        return grand_trines

    def _find_t_square(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find T-square patterns in the aspects.
        
        Args:
            aspects: List of aspects in the birth chart
            
        Returns:
            List of dictionaries containing T-square pattern information
        """
        t_squares = []
        seen_combinations = set()
        
        # Group aspects by type
        squares = [a for a in aspects if str(a["type"]) == "90"]
        oppositions = [a for a in aspects if str(a["type"]) == "180"]
        
        # Check each opposition for potential T-square
        for opp in oppositions:
            planet1 = opp["planet1"].lower()
            planet2 = opp["planet2"].lower()
            
            # Look for squares to both planets in opposition
            for i, sq1 in enumerate(squares):
                sq1_p1 = sq1["planet1"].lower()
                sq1_p2 = sq1["planet2"].lower()
                if sq1_p1 in [planet1, planet2] or sq1_p2 in [planet1, planet2]:
                    for j, sq2 in enumerate(squares):
                        if i != j:
                            sq2_p1 = sq2["planet1"].lower()
                            sq2_p2 = sq2["planet2"].lower()
                            if sq2_p1 in [planet1, planet2] or sq2_p2 in [planet1, planet2]:
                                # Find the apex planet (the one making squares to both opposition planets)
                                apex = None
                                if sq1_p1 == sq2_p1 or sq1_p1 == sq2_p2:
                                    apex = sq1_p1
                                elif sq1_p2 == sq2_p1 or sq1_p2 == sq2_p2:
                                    apex = sq1_p2
                                
                                if apex:
                                    # Create a unique key for this combination
                                    planets = [planet1, planet2, apex]
                                    key = "-".join(sorted(planets))
                                    
                                    if key not in seen_combinations:
                                        seen_combinations.add(key)
                                        t_squares.append({
                                            "planet1": planet1,
                                            "planet2": planet2,
                                            "apex": apex,
                                            "planets": planets
                                        })
        
        return t_squares

    def _find_grand_cross(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Grand Cross patterns in the aspects.
        
        Args:
            aspects: List of aspects in the birth chart
            
        Returns:
            List of dictionaries containing Grand Cross pattern information
        """
        grand_crosses = []
        seen_combinations = set()
        
        # Group aspects by type
        squares = [a for a in aspects if str(a["type"]) == "90"]
        oppositions = [a for a in aspects if str(a["type"]) == "180"]
        
        # Check each pair of oppositions for potential Grand Cross
        for i, opp1 in enumerate(oppositions):
            planet1 = opp1["planet1"].lower()
            planet2 = opp1["planet2"].lower()
            
            for j, opp2 in enumerate(oppositions):
                if i != j:  # Different oppositions
                    planet3 = opp2["planet1"].lower()
                    planet4 = opp2["planet2"].lower()
                    
                    # Check if all four planets are different
                    planets = {planet1, planet2, planet3, planet4}
                    if len(planets) != 4:
                        continue
                        
                    # Check if all four planets form squares with their adjacent planets
                    has_square_13 = any(
                        (a["planet1"].lower() == planet1 and a["planet2"].lower() == planet3) or
                        (a["planet1"].lower() == planet3 and a["planet2"].lower() == planet1)
                        for a in squares
                    )
                    has_square_14 = any(
                        (a["planet1"].lower() == planet1 and a["planet2"].lower() == planet4) or
                        (a["planet1"].lower() == planet4 and a["planet2"].lower() == planet1)
                        for a in squares
                    )
                    has_square_23 = any(
                        (a["planet1"].lower() == planet2 and a["planet2"].lower() == planet3) or
                        (a["planet1"].lower() == planet3 and a["planet2"].lower() == planet2)
                        for a in squares
                    )
                    has_square_24 = any(
                        (a["planet1"].lower() == planet2 and a["planet2"].lower() == planet4) or
                        (a["planet1"].lower() == planet4 and a["planet2"].lower() == planet2)
                        for a in squares
                    )
                    
                    if has_square_13 and has_square_14 and has_square_23 and has_square_24:
                        # Create a unique key for this combination using sorted planet names
                        key = "-".join(sorted([planet1, planet2, planet3, planet4]))
                        if key not in seen_combinations:
                            seen_combinations.add(key)
                            planets_list = sorted([planet1, planet2, planet3, planet4])
                            # Get the modality of the grand cross
                            modality = self._get_cross_modality(planets_list)
                            grand_crosses.append({
                                "planet1": planets_list[0],
                                "planet2": planets_list[1],
                                "planet3": planets_list[2],
                                "planet4": planets_list[3],
                                "planets": planets_list,
                                "modality": modality if modality else "unknown"
                            })
                        
        return grand_crosses

    def _get_cross_modality(self, planets: List[str]) -> Optional[str]:
        """Get the modality of a grand cross based on the signs of the planets."""
        planet_signs = []
        for planet in planets:
            planet_data = self.planets_data.get(planet.lower(), {})
            if "sign" in planet_data:
                planet_signs.append(planet_data["sign"].lower())
        
        if len(planet_signs) != 4:
            return None
        
        # Check if all signs are of the same modality
        modalities = {self.signs_data.get(sign, {}).get("modality") for sign in planet_signs}
        if len(modalities) == 1:
            return next(iter(modalities))
        
        return None

    def _get_trine_element(self, planets: List[str]) -> Optional[str]:
        """Get the element of a grand trine based on the signs of the planets."""
        planet_signs = []
        for planet in planets:
            planet_data = self.planets_data.get(planet.lower(), {})
            if "sign" in planet_data:
                planet_signs.append(planet_data["sign"].lower())
        
        if len(planet_signs) != 3:
            return None
        
        # Check if all signs are of the same element
        elements = {self.signs_data.get(sign, {}).get("element") for sign in planet_signs}
        if len(elements) == 1:
            return next(iter(elements))
        
        return None

    def _get_planet_dignity(self, planet: str, sign: str, house: int) -> Dict[str, Any]:
        """Calculate the dignity of a planet in a sign and house.
        
        Args:
            planet: Planet name
            sign: Sign name
            house: House number
            
        Returns:
            Dictionary with dignity information
        """
        try:
            # Normalize inputs
            planet = self._normalize_planet_name(planet)
            sign = self._normalize_sign_name(sign)
            
            # Get essential and accidental dignities
            essential = self._get_essential_dignity(planet, sign)
            accidental = self._get_accidental_dignity(planet, house)
            
            # Calculate overall strength
            strength = self._calculate_dignity_strength(essential, accidental)
            
            # Get interpretation
            interpretation = self._get_dignity_interpretation(planet, essential, accidental, strength)
        
            return {
                "planet": planet,
                "sign": sign,
                "house": house,
                "essential_dignity": essential,
                "accidental_dignity": accidental,
                "strength": strength,
                "interpretation": interpretation
            }
        except Exception as e:
            self.logger.error(f"Error calculating planet dignity: {str(e)}")
            return {
                "planet": planet,
                "sign": sign,
                "house": house,
                "essential_dignity": "unknown",
                "accidental_dignity": "unknown",
                "strength": 0,
                "interpretation": "Unable to calculate dignity."
            }

    def _get_essential_dignity(self, planet: str, sign: str) -> Dict[str, Any]:
        """Get the essential dignity of a planet in a sign."""
        # Get planet's ruling signs
        ruling_signs = self.dignities_data.get(planet, {}).get("ruling_signs", [])
        exaltation_signs = self.dignities_data.get(planet, {}).get("exaltation_signs", [])
        detriment_signs = self.dignities_data.get(planet, {}).get("detriment_signs", [])
        fall_signs = self.dignities_data.get(planet, {}).get("fall_signs", [])
        
        dignity_type = "neutral"
        if sign in ruling_signs:
            dignity_type = "rulership"
        elif sign in exaltation_signs:
            dignity_type = "exaltation"
        elif sign in detriment_signs:
            dignity_type = "detriment"
        elif sign in fall_signs:
            dignity_type = "fall"
        
        return {
            "type": dignity_type,
            "strength": self._get_essential_dignity_strength(dignity_type)
        }

    def _get_accidental_dignity(self, planet: str, house: int) -> Dict[str, Any]:
        """Get the accidental dignity of a planet based on its house position."""
        # Angular houses (1, 4, 7, 10) give strongest accidental dignity
        # Succedent houses (2, 5, 8, 11) give moderate accidental dignity
        # Cadent houses (3, 6, 9, 12) give weakest accidental dignity
        
        house_type = "cadent"
        if house in [1, 4, 7, 10]:
            house_type = "angular"
        elif house in [2, 5, 8, 11]:
            house_type = "succedent"
        
        return {
            "type": house_type,
            "strength": self._get_accidental_dignity_strength(house_type)
        }

    def _get_essential_dignity_strength(self, dignity_type: str) -> float:
        """Get the strength value for essential dignity."""
        strengths = {
            "rulership": 1.0,
            "exaltation": 0.8,
            "detriment": -0.5,
            "fall": -0.8,
            "neutral": 0.0
        }
        return strengths.get(dignity_type, 0.0)

    def _get_accidental_dignity_strength(self, house_type: str) -> float:
        """Get the strength value for accidental dignity."""
        strengths = {
            "angular": 0.8,
            "succedent": 0.4,
            "cadent": 0.2
        }
        return strengths.get(house_type, 0.0)

    def _calculate_dignity_strength(self, essential: Dict[str, Any], accidental: Dict[str, Any]) -> float:
        """Calculate overall dignity strength combining essential and accidental dignity."""
        return essential["strength"] + accidental["strength"]

    def _get_dignity_interpretation(self, planet: str, essential: Dict[str, Any], accidental: Dict[str, Any], strength: float) -> str:
        """Get interpretation of planetary dignity."""
        interpretations = []
        
        # Essential dignity interpretation
        if essential["type"] == "rulership":
            interpretations.append(f"{planet.capitalize()} is in its ruling sign, giving it strong natural expression.")
        elif essential["type"] == "exaltation":
            interpretations.append(f"{planet.capitalize()} is exalted, enhancing its positive qualities.")
        elif essential["type"] == "detriment":
            interpretations.append(f"{planet.capitalize()} is in detriment, challenging its natural expression.")
        elif essential["type"] == "fall":
            interpretations.append(f"{planet.capitalize()} is in fall, making its expression more difficult.")
        
        # Accidental dignity interpretation
        if accidental["type"] == "angular":
            interpretations.append(f"Being in an angular house strengthens its influence in the chart.")
        elif accidental["type"] == "succedent":
            interpretations.append(f"Being in a succedent house provides moderate influence.")
        elif accidental["type"] == "cadent":
            interpretations.append(f"Being in a cadent house makes its influence more subtle.")
        
        # Overall strength interpretation
        if strength >= 1.5:
            interpretations.append("This is a very strong placement in the chart.")
        elif strength >= 1.0:
            interpretations.append("This is a strong placement in the chart.")
        elif strength >= 0.5:
            interpretations.append("This is a moderately strong placement in the chart.")
        elif strength <= -0.5:
            interpretations.append("This is a challenging placement in the chart.")
        
        return " ".join(interpretations)

    def _get_compatibility_interpretation(self, planet: str, sign: str) -> str:
        """Get interpretation of compatibility between planet and sign.
        
        Args:
            planet: Planet name (normalized)
            sign: Sign name (normalized)
            
        Returns:
            Compatibility interpretation or empty string if not available
        """
        try:
            # Skip if planet or sign is missing
            if not planet or not sign:
                return ""
                
            # Get planet data
            planet_data = self._planet_cache.get(planet, {})
            if not planet_data:
                return ""
                
            # Check if this planet has compatibility data
            if "compatible_signs" not in planet_data:
                return ""
                
            # Get compatible signs for this planet
            compatible_signs = [s.lower() for s in planet_data.get("compatible_signs", [])]
            
            # Generate interpretation based on compatibility
            if sign in compatible_signs:
                return f"This is a harmonious placement that enhances your natural abilities."
            else:
                return f"This placement may present challenges that lead to growth through adaptation."
        except Exception as e:
            self.logger.error(f"Error in compatibility interpretation: {str(e)}")
        return ""

    def _get_aspect_interpretations(self, birth_chart: dict, level: str = "basic") -> dict:
        """Get interpretations for all aspects in the birth chart."""
        interpretations = []
        for aspect in birth_chart.get("aspects", []):
            planet1 = aspect.get("planet1", "")
            planet2 = aspect.get("planet2", "")
            aspect_type = aspect.get("type", "")
            orb = aspect.get("orb", 0.0)
            
            if planet1 and planet2 and aspect_type:
                interpretation = self._get_aspect_interpretation(
                    aspect_type, planet1, planet2, orb, birth_chart, level
                )
                interpretations.append({
                    "planet1": planet1,
                    "planet2": planet2,
                    "type": aspect_type,
                    "interpretation": interpretation
                })
        
        return interpretations

    def _analyze_element_modality_balance(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the balance of elements and modalities in the birth chart."""
        planets = birth_chart.get("planets", {})
        
        # Initialize counters
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
        
        # Count elements and modalities
        for planet, data in planets.items():
            sign = data.get("sign", "").lower()
            if sign in self.signs_data:
                sign_data = self.signs_data[sign]
                element = sign_data.get("element", "").lower()
                modality = sign_data.get("modality", "").lower()
                
                if element in elements:
                    elements[element] += 1
                if modality in modalities:
                    modalities[modality] += 1
        
        # Calculate percentages
        total_planets = sum(elements.values())
        element_percentages = {
            element: (count / total_planets * 100) if total_planets > 0 else 0
            for element, count in elements.items()
        }
        
        modality_percentages = {
            modality: (count / total_planets * 100) if total_planets > 0 else 0
            for modality, count in modalities.items()
        }
        
        # Determine dominant and lacking elements/modalities
        dominant_elements = [e for e, c in elements.items() if c == max(elements.values())]
        lacking_elements = [e for e, c in elements.items() if c == 0]
        
        dominant_modalities = [m for m, c in modalities.items() if c == max(modalities.values())]
        lacking_modalities = [m for m, c in modalities.items() if c == 0]
        
        # Generate interpretation
        interpretation = self._get_element_modality_interpretation(
            elements, modalities,
            element_percentages, modality_percentages,
            dominant_elements, lacking_elements,
            dominant_modalities, lacking_modalities
        )
        
        return {
            "counts": {
                "elements": elements,
                "modalities": modalities
            },
            "percentages": {
                "elements": element_percentages,
                "modalities": modality_percentages
            },
            "dominant": {
                "elements": dominant_elements,
                "modalities": dominant_modalities
            },
            "lacking": {
                "elements": lacking_elements,
                "modalities": lacking_modalities
            },
            "interpretation": interpretation
        }

    def _get_element_modality_interpretation(
        self,
        elements: Dict[str, int],
        modalities: Dict[str, int],
        element_percentages: Dict[str, float],
        modality_percentages: Dict[str, float],
        dominant_elements: List[str],
        lacking_elements: List[str],
        dominant_modalities: List[str],
        lacking_modalities: List[str]
    ) -> str:
        """Generate interpretation of element and modality balance."""
        interpretations = []
        
        # Element balance interpretation
        if len(dominant_elements) == 1:
            interpretations.append(f"The chart shows a strong emphasis on {dominant_elements[0]} element.")
        elif len(dominant_elements) == 2:
            interpretations.append(f"The chart shows a balance between {dominant_elements[0]} and {dominant_elements[1]} elements.")
        
        if lacking_elements:
            interpretations.append(f"The chart lacks {', '.join(lacking_elements)} elements, suggesting areas for potential growth.")
        
        # Modality balance interpretation
        if len(dominant_modalities) == 1:
            interpretations.append(f"The chart shows a strong emphasis on {dominant_modalities[0]} modality.")
        elif len(dominant_modalities) == 2:
            interpretations.append(f"The chart shows a balance between {dominant_modalities[0]} and {dominant_modalities[1]} modalities.")
        
        if lacking_modalities:
            interpretations.append(f"The chart lacks {', '.join(lacking_modalities)} modality, suggesting areas for potential development.")
        
        # Add specific element-modality combinations
        for element in dominant_elements:
            for modality in dominant_modalities:
                key = f"{element}_{modality}"
                if key in self._element_modality_cache:
                    qualities = self._element_modality_cache[key]["qualities"]
                    keywords = self._element_modality_cache[key]["keywords"]
                    interpretations.append(
                        f"The combination of {element} element and {modality} modality suggests "
                        f"{', '.join(qualities)} qualities, with emphasis on {', '.join(keywords)}."
                    )
        
        return " ".join(interpretations)

    def _analyze_quadrant_emphasis(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the emphasis on different quadrants of the chart."""
        planets = birth_chart.get("planets", {})
        
        # Initialize quadrant counters
        quadrants = {
            "north": 0,  # Houses 10-12
            "east": 0,   # Houses 1-3
            "south": 0,  # Houses 4-6
            "west": 0    # Houses 7-9
        }
        
        # Count planets in each quadrant
        for planet, data in planets.items():
            house = data.get("house")
            if house:
                if 10 <= house <= 12:
                    quadrants["north"] += 1
                elif 1 <= house <= 3:
                    quadrants["east"] += 1
                elif 4 <= house <= 6:
                    quadrants["south"] += 1
                elif 7 <= house <= 9:
                    quadrants["west"] += 1
        
        # Calculate percentages
        total_planets = sum(quadrants.values())
        quadrant_percentages = {
            quadrant: (count / total_planets * 100) if total_planets > 0 else 0
            for quadrant, count in quadrants.items()
        }
        
        # Determine dominant quadrants
        dominant_quadrants = [q for q, c in quadrants.items() if c == max(quadrants.values())]
        
        # Generate interpretation
        interpretation = self._get_quadrant_interpretation(quadrants, quadrant_percentages, dominant_quadrants)
        
        return {
            "counts": quadrants,
            "percentages": quadrant_percentages,
            "dominant": dominant_quadrants,
            "interpretation": interpretation
        }

    def _get_quadrant_interpretation(
        self,
        quadrants: Dict[str, int],
        percentages: Dict[str, float],
        dominant_quadrants: List[str]
    ) -> str:
        """Generate interpretation of quadrant emphasis."""
        interpretations = []
        
        # Quadrant emphasis interpretation
        if len(dominant_quadrants) == 1:
            quadrant = dominant_quadrants[0]
            percentage = percentages[quadrant]
            
            if quadrant == "north":
                interpretations.append(
                    f"With {percentage:.1f}% of planets in the northern hemisphere, "
                    "the chart shows a strong emphasis on public life, career, and social standing."
                )
            elif quadrant == "east":
                interpretations.append(
                    f"With {percentage:.1f}% of planets in the eastern hemisphere, "
                    "the chart shows a strong emphasis on personal initiative and self-expression."
                )
            elif quadrant == "south":
                interpretations.append(
                    f"With {percentage:.1f}% of planets in the southern hemisphere, "
                    "the chart shows a strong emphasis on personal life, home, and relationships."
                )
            elif quadrant == "west":
                interpretations.append(
                    f"With {percentage:.1f}% of planets in the western hemisphere, "
                    "the chart shows a strong emphasis on relationships, partnerships, and others."
                )
        
        # Add specific quadrant combinations
        if len(dominant_quadrants) == 2:
            interpretations.append(
                f"The chart shows a balance between {dominant_quadrants[0]} and {dominant_quadrants[1]} quadrants, "
                "suggesting a well-rounded approach to life."
            )
        
        return " ".join(interpretations)

    def _analyze_patterns(self, birth_chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze birth chart for astrological patterns.
        
        Args:
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            List of patterns found in the chart
        """
        patterns = []
        planets = birth_chart.get("planets", {})
        aspects = birth_chart.get("aspects", [])
        
        # Track unique patterns using string keys
        seen_patterns = set()
        
        # Find stelliums (3 or more planets in the same sign)
        sign_planets = {}
        for planet, data in planets.items():
            if planet in ["Ascendant", "Midheaven"]:
                continue
            sign = data.get("sign")
            if sign:
                if sign not in sign_planets:
                    sign_planets[sign] = []
                sign_planets[sign].append(planet.lower())
        
        for sign, planet_list in sign_planets.items():
            if len(planet_list) >= 3:
                # Create a unique key for this stellium
                key = f"stellium-{sign}-{'-'.join(sorted(planet_list))}"
                if key not in seen_patterns:
                    seen_patterns.add(key)
                    patterns.append({
                        "type": "stellium",
                        "planets": planet_list,
                        "sign": sign,
                        "interpretation": f"A stellium in {sign} with {', '.join(planet_list)} indicates a strong focus of energy in this sign."
                    })
        
        # Find T-squares
        t_squares = self._find_t_square(aspects)
        for t_square in t_squares:
            # Create a unique key for this T-square
            key = f"t_square-{'-'.join(sorted([p.lower() for p in t_square['planets']]))}"
            if key not in seen_patterns:
                seen_patterns.add(key)
                patterns.append({
                    "type": "t_square",
                    "planets": t_square["planets"],
                    "apex": t_square["apex"],
                    "interpretation": f"A T-square involving {', '.join(t_square['planets'])} with {t_square['apex']} at the apex indicates dynamic tension seeking resolution."
                })
        
        # Find Grand Trines
        grand_trines = self._find_grand_trine(aspects)
        for grand_trine in grand_trines:
            # Create a unique key for this Grand Trine
            key = f"grand_trine-{'-'.join(sorted([p.lower() for p in grand_trine['planets']]))}"
            if key not in seen_patterns:
                seen_patterns.add(key)
                patterns.append({
                    "type": "grand_trine",
                    "planets": grand_trine["planets"],
                    "interpretation": f"A Grand Trine involving {', '.join(grand_trine['planets'])} indicates natural talents and harmonious energy flow."
                })
        
        # Find Grand Crosses
        grand_crosses = self._find_grand_cross(aspects)
        for cross in grand_crosses:
            # Create a unique key for this Grand Cross
            key = f"grand_cross-{'-'.join(sorted([p.lower() for p in cross['planets']]))}"
            if key not in seen_patterns:
                seen_patterns.add(key)
                patterns.append({
                    "type": "grand_cross",
                    "planets": cross["planets"],
                    "modality": cross["modality"],
                    "interpretation": f"A Grand Cross in {cross['modality']} signs involving {', '.join(cross['planets'])} indicates a complex dynamic of challenges and opportunities for growth."
                })
        
        return patterns

    def _analyze_combinations(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze significant planetary combinations in the birth chart."""
        planets = birth_chart.get("planets", {})
        aspects = birth_chart.get("aspects", [])
        
        combinations = {
            "mutual_receptions": [],
            "planetary_pairs": [],
            "aspect_patterns": [],
            "midpoints": []
        }
        
        # Track unique combinations using string keys
        seen_combinations = set()
        
        # Find mutual receptions (planets in each other's ruling signs)
        for planet1, data1 in planets.items():
            if planet1 in ["Ascendant", "Midheaven"]:
                continue
            sign1 = data1.get("sign", "").lower()
            
            for planet2, data2 in planets.items():
                if planet2 in ["Ascendant", "Midheaven"] or planet1 >= planet2:
                    continue
                sign2 = data2.get("sign", "").lower()
                
                # Check if planets rule each other's signs
                if (sign1 in self.dignities_data.get(planet2.lower(), {}).get("ruling_signs", []) and
                    sign2 in self.dignities_data.get(planet1.lower(), {}).get("ruling_signs", [])):
                    # Create a unique key for this combination
                    key = f"mutual_reception-{'-'.join(sorted([planet1.lower(), planet2.lower()]))}"
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        combinations["mutual_receptions"].append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "sign1": sign1,
                            "sign2": sign2
                        })
        
        # Find significant planetary pairs (planets in aspect with special relationships)
        for aspect in aspects:
            planet1 = aspect["planet1"].lower()
            planet2 = aspect["planet2"].lower()
            aspect_type = str(aspect["type"]).lower() if aspect["type"] is not None else ""
            
            if aspect_type in ["0", "60", "120"]:  # Conjunction, sextile, trine
                # Check if planets have special relationships (dispositor, exaltation, etc.)
                planet1_sign = planets[planet1]["sign"].lower()
                planet2_sign = planets[planet2]["sign"].lower()
                
                if (planet1_sign in self.dignities_data.get(planet2, {}).get("ruling_signs", []) or
                    planet2_sign in self.dignities_data.get(planet1, {}).get("ruling_signs", [])):
                    # Create a unique key for this combination
                    key = f"planetary_pair-{'-'.join(sorted([planet1, planet2]))}-{aspect_type}"
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        combinations["planetary_pairs"].append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect_type": aspect_type,
                            "relationship": "dispositor"
                        })
        
        # Find aspect patterns (midpoints, parallel aspects, etc.)
        for i, aspect1 in enumerate(aspects):
            planet1 = aspect1["planet1"].lower()
            planet2 = aspect1["planet2"].lower()
            aspect_type1 = str(aspect1["type"]).lower() if aspect1["type"] is not None else ""
            
            # Check for midpoint structures
            for j, aspect2 in enumerate(aspects):
                if i != j and aspect2["planet1"].lower() == planet1 and aspect_type1 == str(aspect2["type"]).lower():
                    # Found a midpoint structure
                    midpoint = self._calculate_midpoint(
                        planets[planet2]["degree"],
                        planets[aspect2["planet2"].lower()]["degree"]
                    )
                    # Create a unique key for this midpoint
                    key = f"midpoint-{'-'.join(sorted([planet2.lower(), aspect2['planet2'].lower()]))}-{planet1.lower()}"
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        combinations["midpoints"].append({
                            "planet1": planet2,
                            "planet2": aspect2["planet2"],
                            "midpoint_planet": planet1,
                            "midpoint_degree": midpoint
                        })
        
        return combinations

    def _analyze_house_emphasis(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the emphasis of planets in different houses."""
        planets = birth_chart.get("planets", {})
        
        # Initialize counters for different house types
        house_counts = {
            "angular": {"houses": [1, 4, 7, 10], "count": 0, "planets": []},
            "succedent": {"houses": [2, 5, 8, 11], "count": 0, "planets": []},
            "cadent": {"houses": [3, 6, 9, 12], "count": 0, "planets": []}
        }
        
        # Count planets in each house type
        for planet, data in planets.items():
            if planet in ["Ascendant", "Midheaven"]:
                continue
            house = data.get("house")
            if house:
                for house_type, info in house_counts.items():
                    if house in info["houses"]:
                        info["count"] += 1
                        info["planets"].append(planet)
        
        # Determine emphasis
        total_planets = sum(info["count"] for info in house_counts.values())
        emphasis = []
        
        if total_planets > 0:
            for house_type, info in house_counts.items():
                percentage = (info["count"] / total_planets) * 100
                if percentage >= 40:  # Significant emphasis
                    emphasis.append({
                        "type": house_type,
                        "count": info["count"],
                        "percentage": percentage,
                        "planets": info["planets"],
                        "interpretation": self._get_house_emphasis_interpretation(house_type, info["planets"])
                    })
        
        return {
            "counts": house_counts,
            "emphasis": emphasis
        }
    
    def _get_house_emphasis_interpretation(self, house_type: str, planets: List[str]) -> str:
        """Get interpretation for house emphasis."""
        planet_list = ", ".join(planets)
        
        if house_type == "angular":
            return f"Strong emphasis on angular houses with {planet_list} indicates a proactive and dynamic approach to life. You tend to initiate action and have a strong impact on your environment."
        elif house_type == "succedent":
            return f"Emphasis on succedent houses with {planet_list} suggests a focus on stability, resources, and maintaining what has been established. You excel at building and consolidating."
        else:  # cadent
            return f"Emphasis on cadent houses with {planet_list} indicates adaptability, mental activity, and communication. You are versatile and learn from experiences."

    def _analyze_special_configurations(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze special configurations in the birth chart."""
        planets = birth_chart.get("planets", {})
        aspects = birth_chart.get("aspects", [])
        
        configurations = {
            "stelliums": [],
            "t_squares": [],
            "grand_trines": [],
            "yods": [],
            "mystic_rectangles": [],
            "kites": []
        }
        
        # Track unique planet combinations using a single set with prefixed keys
        seen_combinations = set()
        
        # Find stelliums (3 or more planets in the same sign)
        sign_planets = {}
        for planet, data in planets.items():
            if planet in ["Ascendant", "Midheaven"]:
                continue
            sign = data.get("sign")
            if sign:
                if sign not in sign_planets:
                    sign_planets[sign] = []
                sign_planets[sign].append(planet.lower())
        
        for sign, planet_list in sign_planets.items():
            if len(planet_list) >= 3:
                # Create a unique key for this stellium
                key = f"stellium-{sign}-{'-'.join(sorted(planet_list))}"
                if key not in seen_combinations:
                    seen_combinations.add(key)
                    configurations["stelliums"].append({
                        "sign": sign,
                        "planets": planet_list,
                        "interpretation": self._get_stellium_interpretation(sign, planet_list)
                    })
        
        # Find T-squares
        t_squares = self._find_t_square(aspects)
        for t_square in t_squares:
            # Create a unique key for this T-square
            key = f"t_square-{'-'.join(sorted([p.lower() for p in t_square['planets']]))}"
            if key not in seen_combinations:
                seen_combinations.add(key)
                configurations["t_squares"].append({
                    "planets": t_square["planets"],
                    "interpretation": self._get_t_square_interpretation(t_square["planets"])
                })
        
        # Find Grand Trines
        for aspect in aspects:
            if str(aspect["type"]).lower() == "120":  # Trine
                planet1 = aspect["planet1"].lower()
                planet2 = aspect["planet2"].lower()
                grand_trines = self._find_grand_trine(aspects)
                for grand_trine in grand_trines:
                    if planet1 in [p.lower() for p in grand_trine["planets"]] and planet2 in [p.lower() for p in grand_trine["planets"]]:
                        # Create a unique key for this Grand Trine
                        key = f"grand_trine-{'-'.join(sorted([p.lower() for p in grand_trine['planets']]))}"
                        if key not in seen_combinations:
                            seen_combinations.add(key)
                            configurations["grand_trines"].append({
                                "planets": grand_trine["planets"],
                                "interpretation": self._get_grand_trine_interpretation(grand_trine["planets"])
                            })
        
        # Find Yods
        for aspect in aspects:
            if str(aspect["type"]).lower() == "60":  # Sextile
                planet1 = aspect["planet1"].lower()
                planet2 = aspect["planet2"].lower()
                
                # Look for quincunxes to a third planet
                quincunx_planets = []
                for other_aspect in aspects:
                    if str(other_aspect["type"]).lower() == "150":  # Quincunx
                        other_planet1 = other_aspect["planet1"].lower()
                        other_planet2 = other_aspect["planet2"].lower()
                        
                        if other_planet1 == planet1 and other_planet2 not in [planet1, planet2]:
                            quincunx_planets.append(other_planet2)
                        elif other_planet2 == planet1 and other_planet1 not in [planet1, planet2]:
                            quincunx_planets.append(other_planet1)
                        elif other_planet1 == planet2 and other_planet2 not in [planet1, planet2]:
                            quincunx_planets.append(other_planet2)
                        elif other_planet2 == planet2 and other_planet1 not in [planet1, planet2]:
                            quincunx_planets.append(other_planet1)
                
                for apex_planet in quincunx_planets:
                    # Create a unique key for this Yod
                    key = f"yod-{'-'.join(sorted([planet1, planet2, apex_planet]))}"
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        configurations["yods"].append({
                            "planets": [planet1, planet2, apex_planet],
                            "apex": apex_planet,
                            "interpretation": self._get_yod_interpretation([planet1, planet2, apex_planet])
                        })
        
        return configurations
    
    def _get_stellium_interpretation(self, sign: str, planets: List[str]) -> str:
        """Get interpretation for a stellium."""
        planet_list = ", ".join(planets)
        sign_data = self.signs_data.get(sign.lower(), {})
        element = sign_data.get("element", "").capitalize()
        modality = sign_data.get("modality", "").capitalize()
        
        return (f"Stellium in {sign} with {planet_list}. This concentration of energy in {element} {modality} sign "
                f"indicates a strong focus on {sign_data.get('qualities', {}).get('general', '')}.")
    
    def _get_t_square_interpretation(self, planets: List[str]) -> str:
        """Get interpretation for a T-square."""
        planet_list = ", ".join(planets)
        return (f"T-square involving {planet_list}. This dynamic configuration creates tension and drive for achievement. "
                f"The apex planet acts as a point of release for the energy of the opposition.")
    
    def _get_grand_trine_interpretation(self, planets: List[str]) -> str:
        """Get interpretation for a Grand Trine."""
        planet_list = ", ".join(planets)
        return (f"Grand Trine involving {planet_list}. This harmonious configuration indicates natural talents and easy flow "
                f"of energy between the planets involved, though it may need conscious effort to fully utilize.")
    
    def _get_yod_interpretation(self, planets: List[str]) -> str:
        """Get interpretation for a Yod."""
        planet_list = ", ".join(planets)
        return (f"Yod (Finger of God) involving {planet_list}. This configuration suggests a special mission or purpose, "
                f"with the apex planet indicating the area of life where this manifests.")

    def _format_planet_interpretation(self, planet_data: Dict, sign_data: Dict, house: int, level: str = "basic") -> str:
        """Format planet interpretation."""
        planet_qualities = planet_data.get("qualities", {}).get("general", "")
        sign_qualities = sign_data.get("qualities", {}).get("general", "")
        
        interpretation = []
        interpretation.append(f"Planet in {sign_data.get('name', '')} represents {planet_qualities} expressed through {sign_qualities}.")
        
        if level == "detailed":
            element = sign_data.get("element", "")
            modality = sign_data.get("modality", "")
            keywords = sign_data.get("keywords", [])
            
            if element:
                interpretation.append(f"Element: {element.capitalize()}")
            if modality:
                interpretation.append(f"Modality: {modality.capitalize()}")
            if keywords:
                interpretation.append(f"Keywords: {', '.join(keywords)}")
        
        return " ".join(interpretation)

    def _format_house_interpretation(self, house_data: Dict, sign_data: Dict, level: str = "basic") -> str:
        """Format house interpretation."""
        house_qualities = house_data.get("qualities", {}).get("general", "")
        sign_qualities = sign_data.get("qualities", {}).get("general", "")
        
        interpretation = []
        interpretation.append(f"House in {sign_data.get('name', '')} represents {house_qualities} manifested with {sign_qualities} qualities.")
        
        if level == "detailed":
            element = sign_data.get("element", "")
            modality = sign_data.get("modality", "")
            house_keywords = house_data.get("keywords", [])
            sign_keywords = sign_data.get("keywords", [])
            
            if element:
                interpretation.append(f"Element: {element.capitalize()}")
            if modality:
                interpretation.append(f"Modality: {modality.capitalize()}")
            if house_keywords:
                interpretation.append(f"House Keywords: {', '.join(house_keywords)}")
            if sign_keywords:
                interpretation.append(f"Sign Keywords: {', '.join(sign_keywords)}")
        
        return " ".join(interpretation)

    def _get_aspect_interpretation(self, aspect_type: Union[str, int], planet1: str, planet2: str, orb: float, birth_chart: Dict[str, Any], level: str = "basic") -> str:
        """Get interpretation for a planetary aspect.
        
        This method provides detailed interpretations of planetary aspects,
        including retrograde influences, house contexts, and aspect patterns.
        
        Args:
            aspect_type: Type of aspect (numeric or string)
            planet1: First planet in the aspect
            planet2: Second planet in the aspect
            orb: Orb of the aspect
            birth_chart: Dictionary containing birth chart data
            level: Level of interpretation detail ("basic" or "detailed")
            
        Returns:
            Detailed interpretation string
        """
        try:
            # Normalize planet names
            planet1 = self._normalize_planet_name(planet1)
            planet2 = self._normalize_planet_name(planet2)
            
            # Ensure planets exist in the system
            if not self._validate_planet(planet1) or not self._validate_planet(planet2):
                return ""

            # Convert aspect type to a normalized format
            aspect_mapping = {
                "0": "conjunction",
                "60": "sextile",
                "90": "square",
                "120": "trine",
                "180": "opposition",
                "conjunction": "conjunction",
                "sextile": "sextile",
                "square": "square",
                "trine": "trine",
                "opposition": "opposition"
            }
            
            normalized_aspect = aspect_mapping.get(str(aspect_type).lower(), "")
            if not normalized_aspect:
                return ""
                
            # Get base interpretation
            base_interpretation = self._get_base_aspect_interpretation(planet1, planet2, normalized_aspect)
            if not base_interpretation:
                return ""

            # Build the complete interpretation
            interpretation_parts = [base_interpretation]

            # Add retrograde influence if applicable
            retrograde_influence = self._get_retrograde_influence(planet1, planet2, birth_chart)
            if retrograde_influence:
                interpretation_parts.append(retrograde_influence)

            # Add house context if applicable
            house_context = self._get_house_context_interpretation(planet1, planet2, birth_chart)
            if house_context:
                interpretation_parts.append(house_context)

            # Add aspect pattern context if applicable
            aspect_pattern = self._get_aspect_pattern_interpretation(planet1, planet2, normalized_aspect, birth_chart.get("aspects", []))
            if aspect_pattern:
                interpretation_parts.append(aspect_pattern)

            # Add orb strength interpretation
            orb_strength = self._calculate_orb_strength(orb, normalized_aspect)
            if orb_strength > 0:
                strength_description = "strong" if orb_strength > 0.8 else "moderate" if orb_strength > 0.5 else "weak"
                interpretation_parts.append(f"This aspect has {strength_description} strength.")

            # Add pattern context if applicable
            pattern_context = self._get_pattern_context(planet1, planet2, normalized_aspect, birth_chart)
            if pattern_context:
                interpretation_parts.append(pattern_context)

            # Join all parts with appropriate punctuation
            return " ".join(interpretation_parts)

        except Exception as e:
            self.logger.error(f"Error generating aspect interpretation: {str(e)}")
            return ""

    def _get_retrograde_influence(self, planet1: str, planet2: str, birth_chart: Dict[str, Any]) -> Optional[str]:
        """Get interpretation for retrograde influence on an aspect.
        
        Args:
            planet1: First planet in the aspect
            planet2: Second planet in the aspect
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            Interpretation string for retrograde influence, or None if not applicable
        """
        try:
            planets_data = birth_chart.get("planets", {})
            retrograde_planets = []
            
            # Check if either planet is retrograde
            for planet in [planet1, planet2]:
                if planet.lower() in planets_data:
                    planet_data = planets_data[planet.lower()]
                    if planet_data.get("is_retrograde", False):
                        retrograde_planets.append(planet)
            
            if not retrograde_planets:
                return None
                
            # Get retrograde interpretation
            if len(retrograde_planets) == 2:
                return f"Both {planet1} and {planet2} are retrograde, suggesting internalized energy and a need for reflection in this aspect."
            else:
                planet = retrograde_planets[0]
                return f"{planet} is retrograde, indicating a more internalized expression of this aspect's energy."
                
        except Exception as e:
            self.logger.error(f"Error getting retrograde influence: {str(e)}")
            return None

    def _get_house_context_interpretation(self, planet1: str, planet2: str, birth_chart: Dict[str, Any]) -> Optional[str]:
        """Get interpretation for house context of an aspect.
        
        Args:
            planet1: First planet in the aspect
            planet2: Second planet in the aspect
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            Interpretation string for house context, or None if not applicable
        """
        try:
            planets_data = birth_chart.get("planets", {})
            houses_data = birth_chart.get("houses", {})
            
            # Get house positions for both planets
            house1 = None
            house2 = None
            
            for planet, data in planets_data.items():
                if planet.lower() == planet1.lower():
                    house1 = data.get("house")
                elif planet.lower() == planet2.lower():
                    house2 = data.get("house")
            
            if not (house1 and house2):
                return None
                
            # Get house interpretations
            house1_data = houses_data.get(str(house1), {})
            house2_data = houses_data.get(str(house2), {})
            
            if not (house1_data and house2_data):
                return None
                
            # Get house keywords
            house1_keywords = house1_data.get("keywords", [])
            house2_keywords = house2_data.get("keywords", [])
            
            if not (house1_keywords and house2_keywords):
                return None
                
            # Create house context interpretation
            return f"This aspect connects the {house1_keywords[0]} (House {house1}) with the {house2_keywords[0]} (House {house2}), " \
                   f"linking these areas of life in a meaningful way."
                   
        except Exception as e:
            self.logger.error(f"Error getting house context: {str(e)}")
            return None

    def _get_aspect_pattern_interpretation(self, planet1: str, planet2: str, aspect_type: str, aspects: List[Dict[str, Any]]) -> str:
        """Get interpretation for aspect patterns involving the given aspect.
        
        Args:
            planet1: First planet in the aspect
            planet2: Second planet in the aspect
            aspect_type: Type of aspect
            aspects: List of all aspects in the chart
            
        Returns:
            Interpretation string for aspect patterns
        """
        try:
            # Look for patterns involving this aspect
            patterns = []
            
            # Check for mutual reception
            if aspect_type == "conjunction":
                # Check if planets are in each other's ruling signs
                planet1_sign = self._get_planet_sign(planet1)
                planet2_sign = self._get_planet_sign(planet2)
                
                if planet1_sign and planet2_sign:
                    planet1_rulers = self._get_sign_rulers(planet1_sign)
                    planet2_rulers = self._get_sign_rulers(planet2_sign)
                    
                    if planet2 in planet1_rulers and planet1 in planet2_rulers:
                        patterns.append("mutual reception")
            
            # Check for aspect patterns
            for aspect in aspects:
                if aspect["planet1"].lower() in [planet1.lower(), planet2.lower()] or \
                   aspect["planet2"].lower() in [planet1.lower(), planet2.lower()]:
                    # Skip the current aspect
                    if (aspect["planet1"].lower() == planet1.lower() and aspect["planet2"].lower() == planet2.lower()) or \
                       (aspect["planet2"].lower() == planet1.lower() and aspect["planet1"].lower() == planet2.lower()):
                        continue
                    
                    # Check for aspect patterns
                    if aspect["type"] == "120":  # Trine
                        patterns.append("trine pattern")
                    elif aspect["type"] == "90":  # Square
                        patterns.append("square pattern")
                    elif aspect["type"] == "180":  # Opposition
                        patterns.append("opposition pattern")
            
            if not patterns:
                return ""
                
            return f"This aspect is part of a {', '.join(patterns)}."
            
        except Exception as e:
            self.logger.error(f"Error getting aspect pattern interpretation: {str(e)}")
            return ""

    def _calculate_orb_strength(self, orb: float, aspect_type: str) -> float:
        """Calculate the strength of an aspect based on its orb.
        
        Args:
            orb: Orb of the aspect
            aspect_type: Type of aspect
            
        Returns:
            Strength value between 0 and 1
        """
        try:
            # Define maximum orbs for different aspect types
            max_orbs = {
                "conjunction": 10,
                "sextile": 6,
                "square": 8,
                "trine": 8,
                "opposition": 10
            }
            
            max_orb = max_orbs.get(aspect_type, 8)
            if max_orb == 0:
                return 0
                
            # Calculate strength (1 - (orb / max_orb))
            strength = 1 - (abs(orb) / max_orb)
            return max(0, min(1, strength))
            
        except Exception as e:
            self.logger.error(f"Error calculating orb strength: {str(e)}")
            return 0

    def _get_pattern_context(self, planet1: str, planet2: str, aspect_type: str, birth_chart: Dict[str, Any]) -> str:
        """Get interpretation for pattern context of an aspect.
        
        Args:
            planet1: First planet in the aspect
            planet2: Second planet in the aspect
            aspect_type: Type of aspect
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            Interpretation string for pattern context
        """
        try:
            # Get planet dignities
            planet1_dignity = self._get_planet_dignity(planet1, birth_chart)
            planet2_dignity = self._get_planet_dignity(planet2, birth_chart)
            
            # Get compatibility
            compatibility = self._get_compatibility_interpretation(planet1, planet2)
            
            # Build pattern context
            context_parts = []
            
            # Add dignity context
            if planet1_dignity["strength"] > 0.7 or planet2_dignity["strength"] > 0.7:
                strong_planet = planet1 if planet1_dignity["strength"] > planet2_dignity["strength"] else planet2
                context_parts.append(f"{strong_planet} is particularly strong in this aspect.")
            
            # Add compatibility context
            if compatibility:
                context_parts.append(compatibility)
            
            return " ".join(context_parts)
            
        except Exception as e:
            self.logger.error(f"Error getting pattern context: {str(e)}")
            return ""

    def _calculate_midpoint(self, degree1, degree2):
        """Calculate the midpoint between two degrees."""
        return (degree1 + degree2) / 2

    def _get_base_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: str) -> str:
        """Get the base interpretation for an aspect between two planets.
        
        Args:
            planet1: First planet name (normalized to lowercase)
            planet2: Second planet name (normalized to lowercase)
            aspect_type: Type of aspect (normalized to lowercase)
            
        Returns:
            Base interpretation string
        """
        try:
            # Generate a generic interpretation
            aspect_qualities = {
                "conjunction": "Merging of energies, intensifying the qualities of both planets",
                "opposition": "Tension and awareness between opposing forces",
                "trine": "Harmonious flow and ease of expression",
                "square": "Dynamic tension driving growth and change",
                "sextile": "Opportunities for cooperation and development"
            }
            
            quality = aspect_qualities.get(aspect_type, "")
            if not quality:
                return ""
                
            # Create a readable interpretation
            return f"{aspect_type.title()} between {planet1.title()} and {planet2.title()}: {quality}."
            
        except Exception as e:
            self.logger.error(f"Error creating base aspect interpretation: {str(e)}")
            return ""

    def _analyze_simple_element_balance(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the elemental balance in the birth chart.
        
        This is a simplified version of the element analysis that provides
        detailed insights into elemental combinations and patterns.
        
        Args:
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            Dictionary with element counts and interpretation
        """
        try:
            # Initialize element counts and planet lists
            elements = {
                "fire": 0,
                "earth": 0, 
                "air": 0,
                "water": 0
            }
            
            planets_by_element = {
                "fire": [],
                "earth": [],
                "air": [],
                "water": []
            }
            
            # Process planets
            for planet, data in birth_chart.get("planets", {}).items():
                sign = data.get("sign", "").lower()
                
                # Skip if no sign data
                if not sign:
                    continue
                    
                # Get element for this sign
                element = ""
                if sign in self._sign_cache:
                    element = self._sign_cache[sign].get("element", "").lower()
                    
                if element in elements:
                    elements[element] += 1
                    planets_by_element[element].append(planet)
            
            # Calculate percentages
            total_planets = sum(elements.values())
            percentages = {}
            if total_planets > 0:
                percentages = {
                    element: (count / total_planets * 100)
                    for element, count in elements.items()
                }
            
            # Determine dominant and lacking elements
            dominant_elements = []
            lacking_elements = []
            
            if total_planets > 0:
                max_count = max(elements.values())
                min_count = min(elements.values())
                
                dominant_elements = [e for e, c in elements.items() if c == max_count and c > 0]
                lacking_elements = [e for e, c in elements.items() if c == min_count and c == 0]
            
            # Generate interpretation
            interpretation = self._get_simple_element_interpretation(
                elements, percentages, dominant_elements, lacking_elements, planets_by_element
            )
            
            return {
                "counts": elements,
                "percentages": percentages,
                "dominant": dominant_elements,
                "lacking": lacking_elements,
                "planets_by_element": planets_by_element,
                "interpretation": interpretation
            }
        except Exception as e:
            self.logger.error(f"Error analyzing element balance: {str(e)}", exc_info=True)
            return {
                "counts": {},
                "percentages": {},
                "dominant": [],
                "lacking": [],
                "planets_by_element": {},
                "interpretation": "Element balance analysis unavailable."
            }
    
    def _get_simple_element_interpretation(
        self, 
        elements: Dict[str, int],
        percentages: Dict[str, float],
        dominant_elements: List[str],
        lacking_elements: List[str],
        planets_by_element: Dict[str, List[str]]
    ) -> str:
        """Generate interpretation for element balance.
        
        Args:
            elements: Counts of planets in each element
            percentages: Percentage of planets in each element
            dominant_elements: List of dominant elements
            lacking_elements: List of lacking elements
            planets_by_element: Dictionary mapping elements to lists of planets
            
        Returns:
            Interpretation string
        """
        interpretation_parts = []
        
        # Add dominant element interpretation
        if dominant_elements:
            dominant_element = dominant_elements[0]
            dominant_count = elements[dominant_element]
            dominant_percent = round(percentages[dominant_element])
            dominant_planets = ", ".join(planets_by_element[dominant_element])
            
            element_qualities = {
                "fire": "energetic, passionate, and action-oriented",
                "earth": "practical, grounded, and reliable",
                "air": "intellectual, communicative, and social",
                "water": "emotional, intuitive, and sensitive"
            }
            
            element_challenges = {
                "fire": "patience and planning",
                "earth": "adaptability and change",
                "air": "emotional depth and stability",
                "water": "objectivity and detachment"
            }
            
            dominant_quality = element_qualities.get(dominant_element, "")
            dominant_challenge = element_challenges.get(dominant_element, "")
            
            if dominant_quality:
                interpretation_parts.append(
                    f"Your chart has a strong {dominant_element} element influence ({dominant_percent}%) "
                    f"with {dominant_planets} in {dominant_element} signs. This makes you {dominant_quality}. "
                    f"However, you may need to work on {dominant_challenge}."
                )
        
        # Add lacking element interpretation
        if lacking_elements:
            lacking_element = lacking_elements[0]
            element_challenges = {
                "fire": "initiating action and maintaining enthusiasm",
                "earth": "practicality and grounding yourself",
                "air": "objectivity and communication",
                "water": "emotional processing and intuition"
            }
            
            element_growth = {
                "fire": "developing confidence and taking initiative",
                "earth": "building stability and practical skills",
                "air": "enhancing communication and social connections",
                "water": "deepening emotional awareness and intuition"
            }
            
            lacking_challenge = element_challenges.get(lacking_element, "")
            growth_opportunity = element_growth.get(lacking_element, "")
            
            if lacking_challenge and growth_opportunity:
                interpretation_parts.append(
                    f"Your chart lacks planets in {lacking_element} signs, which may create challenges with {lacking_challenge}. "
                    f"This presents an opportunity for growth in {growth_opportunity}."
                )
        
        # Add elemental combination interpretation
        if len(dominant_elements) > 1:
            combination_qualities = {
                ("fire", "air"): "dynamic and expressive",
                ("fire", "earth"): "practical and ambitious",
                ("fire", "water"): "passionate and intuitive",
                ("earth", "air"): "practical and communicative",
                ("earth", "water"): "stable and nurturing",
                ("air", "water"): "intellectual and empathetic"
            }
            
            combination_key = tuple(sorted(dominant_elements))
            combination_quality = combination_qualities.get(combination_key, "")
            
            if combination_quality:
                interpretation_parts.append(
                    f"The combination of {' and '.join(dominant_elements)} elements makes you {combination_quality}."
                )
        
        # Create final interpretation
        if interpretation_parts:
            return " ".join(interpretation_parts)
        else:
            return "Your chart shows a relatively balanced distribution of elements."

    def _analyze_simple_modality_balance(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the modality balance in the birth chart.
        
        This is a simplified version of the modality analysis that provides
        detailed insights into modality patterns and combinations.
        
        Args:
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            Dictionary with modality counts and interpretation
        """
        try:
            # Initialize modality counts and planet lists
            modalities = {
                "cardinal": 0,
                "fixed": 0,
                "mutable": 0
            }
            
            planets_by_modality = {
                "cardinal": [],
                "fixed": [],
                "mutable": []
            }
            
            # Process planets
            for planet, data in birth_chart.get("planets", {}).items():
                sign = data.get("sign", "").lower()
                
                # Skip if no sign data
                if not sign:
                    continue
                    
                # Get modality for this sign
                modality = ""
                if sign in self._sign_cache:
                    modality = self._sign_cache[sign].get("modality", "").lower()
                    
                if modality in modalities:
                    modalities[modality] += 1
                    planets_by_modality[modality].append(planet)
            
            # Calculate percentages
            total_planets = sum(modalities.values())
            percentages = {}
            if total_planets > 0:
                percentages = {
                    modality: (count / total_planets * 100)
                    for modality, count in modalities.items()
                }
            
            # Determine dominant and lacking modalities
            dominant_modalities = []
            lacking_modalities = []
            
            if total_planets > 0:
                max_count = max(modalities.values())
                min_count = min(modalities.values())
                
                dominant_modalities = [m for m, c in modalities.items() if c == max_count and c > 0]
                lacking_modalities = [m for m, c in modalities.items() if c == min_count and c == 0]
            
            # Generate interpretation
            interpretation = self._get_simple_modality_interpretation(
                modalities, percentages, dominant_modalities, lacking_modalities, planets_by_modality
            )
            
            return {
                "counts": modalities,
                "percentages": percentages,
                "dominant": dominant_modalities,
                "lacking": lacking_modalities,
                "planets_by_modality": planets_by_modality,
                "interpretation": interpretation
            }
        except Exception as e:
            self.logger.error(f"Error analyzing modality balance: {str(e)}", exc_info=True)
            return {
                "counts": {},
                "percentages": {},
                "dominant": [],
                "lacking": [],
                "planets_by_modality": {},
                "interpretation": "Modality balance analysis unavailable."
            }
    
    def _get_simple_modality_interpretation(
        self, 
        modalities: Dict[str, int],
        percentages: Dict[str, float],
        dominant_modalities: List[str],
        lacking_modalities: List[str],
        planets_by_modality: Dict[str, List[str]]
    ) -> str:
        """Generate interpretation for modality balance.
        
        Args:
            modalities: Counts of planets in each modality
            percentages: Percentage of planets in each modality
            dominant_modalities: List of dominant modalities
            lacking_modalities: List of lacking modalities
            planets_by_modality: Dictionary mapping modalities to lists of planets
            
        Returns:
            Interpretation string
        """
        interpretation_parts = []
        
        # Add dominant modality interpretation
        if dominant_modalities:
            dominant_modality = dominant_modalities[0]
            dominant_count = modalities[dominant_modality]
            dominant_percent = round(percentages[dominant_modality])
            dominant_planets = ", ".join(planets_by_modality[dominant_modality])
            
            modality_qualities = {
                "cardinal": "initiative, leadership, and action-oriented",
                "fixed": "stability, determination, and persistence",
                "mutable": "adaptability, flexibility, and versatility"
            }
            
            modality_challenges = {
                "cardinal": "patience and following through",
                "fixed": "adaptability and openness to change",
                "mutable": "focus and commitment"
            }
            
            dominant_quality = modality_qualities.get(dominant_modality, "")
            dominant_challenge = modality_challenges.get(dominant_modality, "")
            
            if dominant_quality:
                interpretation_parts.append(
                    f"Your chart has a strong {dominant_modality} modality influence ({dominant_percent}%) "
                    f"with {dominant_planets} in {dominant_modality} signs. This makes you {dominant_quality}. "
                    f"However, you may need to work on {dominant_challenge}."
                )
        
        # Add lacking modality interpretation
        if lacking_modalities:
            lacking_modality = lacking_modalities[0]
            modality_challenges = {
                "cardinal": "taking initiative and leading",
                "fixed": "maintaining stability and focus",
                "mutable": "adapting to change and being flexible"
            }
            
            modality_growth = {
                "cardinal": "developing leadership and initiative",
                "fixed": "building stability and determination",
                "mutable": "enhancing adaptability and versatility"
            }
            
            lacking_challenge = modality_challenges.get(lacking_modality, "")
            growth_opportunity = modality_growth.get(lacking_modality, "")
            
            if lacking_challenge and growth_opportunity:
                interpretation_parts.append(
                    f"Your chart lacks planets in {lacking_modality} signs, which may create challenges with {lacking_challenge}. "
                    f"This presents an opportunity for growth in {growth_opportunity}."
                )
        
        # Add modality combination interpretation
        if len(dominant_modalities) > 1:
            combination_qualities = {
                ("cardinal", "fixed"): "ambitious and determined",
                ("cardinal", "mutable"): "dynamic and adaptable",
                ("fixed", "mutable"): "stable yet flexible"
            }
            
            combination_key = tuple(sorted(dominant_modalities))
            combination_quality = combination_qualities.get(combination_key, "")
            
            if combination_quality:
                interpretation_parts.append(
                    f"The combination of {' and '.join(dominant_modalities)} modalities makes you {combination_quality}."
                )
        
        # Create final interpretation
        if interpretation_parts:
            return " ".join(interpretation_parts)
        else:
            return "Your chart shows a relatively balanced distribution of modalities."

    def _load_sun_qualities(self):
        """Load sun qualities data from CSV file.
        
        This method reads the sun_qualities.csv file and extracts the most useful
        information for enhancing interpretations.
        """
        try:
            import csv
            from pathlib import Path
            
            sun_qualities_path = Path(__file__).parent.parent.parent / "data" / "sun_qualities.csv"
            
            if not sun_qualities_path.exists():
                self.logger.warning(f"Sun qualities file not found: {sun_qualities_path}")
                return
                
            self.logger.info(f"Loading sun qualities from {sun_qualities_path}")
            
            sun_data = {}
            with open(sun_qualities_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # Get column headers (sign names)
                headers = rows[0][2:]  # Skip first two columns
                
                # Extract key rows
                keyword_row = None
                best_trait_row = None
                for row in rows:
                    if row[0] == "31" and row[1] == "Keywords":
                        keyword_row = row
                    elif row[0] == "16" and row[1] == "Best Trait":
                        best_trait_row = row
                
                if not keyword_row or not best_trait_row:
                    self.logger.warning("Failed to find Keywords or Best Trait rows in sun_qualities.csv")
                    return
                    
                # Process each sign
                for i, sign in enumerate(headers):
                    # Normalize sign name
                    normalized_sign = sign.lower()
                    
                    # Get keywords and traits
                    keywords_str = keyword_row[i+2].strip('[]').replace("'", "").split(', ')
                    best_trait = best_trait_row[i+2]
                    
                    # Store data
                    sun_data[normalized_sign] = {
                        "keywords": keywords_str,
                        "best_trait": best_trait
                    }
            
            # Update sign cache with new qualities
            for sign, data in sun_data.items():
                if sign in self._sign_cache:
                    self._sign_cache[sign]["keywords"] = data["keywords"]
                    self._sign_cache[sign]["best_trait"] = data["best_trait"]
            
            self.logger.info(f"Successfully loaded sun qualities for {len(sun_data)} signs")
            
        except Exception as e:
            self.logger.error(f"Error loading sun qualities: {str(e)}", exc_info=True)