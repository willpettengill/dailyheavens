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
        """Initialize the interpretation service.
        
        This method sets up the internal caches and loads the necessary
        reference data for generating interpretations.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing InterpretationService")
        
        # Initialize caches
        self._planet_cache = {}
        self._sign_cache = {}
        self._house_cache = {}
        self._aspect_cache = {}
        self._combination_cache = {}
        self._pattern_cache = {}
        
        # Load structured data from JSON files
        self.structured_data = {}
        self._load_structured_data()
        
        # Initialize caches for various interpretation components
        self._initialize_caches()
        
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
        """Load structured data from JSON files."""
        try:
            # Define path to structured data directory
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "structured")
            
            # Load each JSON file into structured_data dictionary
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(data_dir, filename)
                    key = filename.replace(".json", "")
                    
                    try:
                        with open(file_path, "r") as f:
                            self.structured_data[key] = json.load(f)
                            self.logger.debug(f"Successfully loaded {filename}")
                    except Exception as e:
                        self.logger.error(f"Error loading {filename}: {str(e)}")
            
            # Convert numeric aspect types to strings for consistency - using a copy to avoid mutation during iteration
            aspect_data = self.structured_data.get("aspects", {})
            aspect_types_to_add = {}
            
            for aspect_type, data in list(aspect_data.items()):
                if "angle" in data:
                    angle = str(data["angle"])
                    aspect_types_to_add[angle] = data
            
            # Add the new aspect types separately
            for angle, data in aspect_types_to_add.items():
                if angle not in aspect_data:
                    aspect_data[angle] = data
            
            self.logger.debug(f"Loaded structured data: {list(self.structured_data.keys())}")
            
            # Check if descriptions is loaded
            if "descriptions" in self.structured_data:
                self.logger.info("Descriptions data loaded successfully")
                self.logger.debug(f"Available signs in descriptions: {list(self.structured_data['descriptions'].keys())}")
            else:
                self.logger.warning("Descriptions data not loaded!")
            
        except Exception as e:
            self.logger.error(f"Error loading structured data: {str(e)}", exc_info=True)

    def _initialize_caches(self):
        """Initialize caches with data from structured_data."""
        try:
            # Initialize planet cache
            planets_data = self.structured_data.get("planets", {})
            if planets_data:
                self._planet_cache = {k.lower(): v for k, v in planets_data.items()}
            
            # Initialize sign cache
            signs_data = self.structured_data.get("signs", {})
            if signs_data:
                self._sign_cache = {k.lower(): v for k, v in signs_data.items()}
            
            # Initialize house cache
            houses_data = self.structured_data.get("houses", {})
            if houses_data:
                self._house_cache = {k: v for k, v in houses_data.items()}
            
            # Initialize aspect cache
            aspects_data = self.structured_data.get("aspects", {})
            if aspects_data:
                self._aspect_cache = {k.lower(): v for k, v in aspects_data.items()}
            
            # Add numeric keys to aspect cache - using a copy to avoid mutation during iteration
            aspect_types_to_add = {}
            
            for aspect_type, data in list(self._aspect_cache.items()):
                if "angle" in data:
                    angle_str = str(data["angle"])
                    aspect_types_to_add[angle_str] = data
            
            # Add the new aspect types separately
            for angle_str, data in aspect_types_to_add.items():
                if angle_str not in self._aspect_cache:
                    self._aspect_cache[angle_str] = data
            
            # Load sun qualities for additional cache
            self._load_sun_qualities()
            
            self.logger.debug("Successfully initialized caches")
        except Exception as e:
            self.logger.error(f"Error initializing caches: {str(e)}", exc_info=True)
    
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
                "combinations": {},
                "summary": ""
            }
            
            # Extract key signs for summary
            sun_sign = None
            moon_sign = None
            rising_sign = None
            
            # Get sun sign
            if "planets" in birth_chart and "sun" in birth_chart["planets"]:
                sun_sign = birth_chart["planets"]["sun"].get("sign", "").lower()
            
            # Get moon sign
            if "planets" in birth_chart and "moon" in birth_chart["planets"]:
                moon_sign = birth_chart["planets"]["moon"].get("sign", "").lower()
            
            # Get rising sign (ascendant)
            if "angles" in birth_chart and "ascendant" in birth_chart["angles"]:
                rising_sign = birth_chart["angles"]["ascendant"].get("sign", "").lower()
            elif "planets" in birth_chart and "ascendant" in birth_chart["planets"]:
                rising_sign = birth_chart["planets"]["ascendant"].get("sign", "").lower()
            
            # Create a summary interpretation from descriptions
            summary_parts = []
            
            # Load descriptions from structured data
            descriptions = self.structured_data.get("descriptions", {})
            
            # Add sun sign description
            if sun_sign and sun_sign in descriptions:
                sun_desc = descriptions[sun_sign].get("sun_sign", "")
                if sun_desc:
                    summary_parts.append(f"Sun in {sun_sign.title()}: {sun_desc}")
            
            # Add moon sign description
            if moon_sign and moon_sign in descriptions:
                moon_desc = descriptions[moon_sign].get("moon_sign", "")
                if moon_desc:
                    summary_parts.append(f"Moon in {moon_sign.title()}: {moon_desc}")
            
            # Add rising sign description
            if rising_sign and rising_sign in descriptions:
                rising_desc = descriptions[rising_sign].get("rising_sign", "")
                if rising_desc:
                    summary_parts.append(f"Rising Sign ({rising_sign.title()}): {rising_desc}")
            
            # Set summary if we have descriptions
            if summary_parts:
                interpretations["summary"] = " ".join(summary_parts)
            
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
            
            # Generate house interpretations using our enhanced method
            house_interpretations = self._get_house_interpretations(birth_chart, level)
            interpretations["houses"] = house_interpretations
            
            # Generate aspect interpretations
            for aspect in birth_chart.get("aspects", []):
                try:
                    planet1 = aspect.get("planet1", "")
                    planet2 = aspect.get("planet2", "")
                    aspect_type = aspect.get("type", "")
                    orb = aspect.get("orb", 0.0)
                    
                    if planet1 and planet2 and aspect_type:
                        # Use our enhanced aspect interpretation method
                        detailed_interp = self._get_aspect_interpretation(
                            aspect_type,
                            planet1,
                            planet2,
                            orb,
                            birth_chart,
                            level
                        )
                        
                        interpretations["aspects"].append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "type": aspect_type,
                            "interpretation": detailed_interp
                        })
                except Exception as e:
                    self.logger.error(f"Error generating aspect interpretation: {str(e)}")
                    continue
            
            # Add patterns if detailed level
            if level == "detailed":
                try:
                    patterns = self._analyze_simple_patterns(birth_chart)
                    interpretations["patterns"] = patterns
                    
                    # Add combinations analysis
                    combinations = self._analyze_combinations(birth_chart)
                    interpretations["combinations"] = combinations
                    
                    # Add element and modality balance if available
                    try:
                        element_balance = self._analyze_simple_element_balance(birth_chart)
                        if element_balance:
                            interpretations["element_balance"] = element_balance
                            
                        modality_balance = self._analyze_simple_modality_balance(birth_chart)
                        if modality_balance:
                            interpretations["modality_balance"] = modality_balance
                    except Exception as e:
                        self.logger.error(f"Error analyzing element/modality: {str(e)}")
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

    def _get_house_interpretations(self, birth_chart: Dict[str, Any], level: str = "basic") -> List[Dict[str, Any]]:
        """Generate interpretations for house placements."""
        interpretations = []
        try:
            houses_data = birth_chart.get("houses", {})
            for house_num in range(1, 13):
                house_key = f"house{house_num}"
                if house_key in houses_data:
                    house_data = houses_data[house_key]
                    sign = house_data.get("sign")
                    if sign:
                        # Get house data from structured data
                        house_info = self.structured_data.get("houses", {}).get(str(house_num), {})
                        sign_info = self.structured_data.get("signs", {}).get(sign.lower(), {})
                        
                        # Get house name and type
                        house_name = house_info.get("name", f"House {house_num}")
                        house_type = house_info.get("type", "")
                        
                        # Get keywords
                        house_keywords = house_info.get("keywords", [])
                        sign_keywords = sign_info.get("keywords", [])
                        
                        # Basic interpretation
                        base_interp = f"House {house_num} ({house_name}) in {sign}"
                        
                        # Add house meaning
                        house_meaning = house_info.get("qualities", {}).get("general", "")
                        if house_meaning:
                            base_interp += f": {house_meaning}"
                        
                        # Add sign influence
                        sign_influence = f"The {sign} influence brings {', '.join(sign_keywords[:3])} to this area of life."
                        
                        # Add detailed interpretation if requested
                        detailed = ""
                        if level == "detailed" and house_keywords:
                            detailed = f" This house represents {', '.join(house_keywords)}."
                        
                        # Check for planets in the house
                        planets = []
                        for planet, data in birth_chart.get("planets", {}).items():
                            if data.get("house") == house_num:
                                planets.append(planet)
                        
                        planets_interp = ""
                        if planets:
                            planets_interp = f" Planets here: {', '.join(planets)}."
                        
                        interpretations.append({
                            "house": house_num,
                            "sign": sign,
                            "planets": planets,
                            "interpretation": f"{base_interp}. {sign_influence}{detailed}{planets_interp}"
                        })
            return interpretations
        except Exception as e:
            self.logger.error(f"Error generating house interpretations: {str(e)}")
            return []

    def _find_grand_trine(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Grand Trine patterns in the aspects.
        
        Args:
            aspects: List of aspects in the birth chart
            
        Returns:
            List of dictionaries containing Grand Trine pattern information
        """
        grand_trines = []
        seen_combinations = set()
        
        # Group aspects by type, normalize numeric aspect types
        trines = []
        
        for aspect in aspects:
            aspect_type = aspect.get("type")
            # Handle numeric or string representation
            if aspect_type in [120, "120", "trine"]:
                trines.append(aspect)
        
        # Check each trine for potential Grand Trine
        for i, trine1 in enumerate(trines):
            planet1 = trine1["planet1"].lower() if isinstance(trine1["planet1"], str) else trine1["planet1"]
            planet2 = trine1["planet2"].lower() if isinstance(trine1["planet2"], str) else trine1["planet2"]
            
            # Look for trines to both planets
            for j, trine2 in enumerate(trines):
                if i != j:
                    trine2_p1 = trine2["planet1"].lower() if isinstance(trine2["planet1"], str) else trine2["planet1"]
                    trine2_p2 = trine2["planet2"].lower() if isinstance(trine2["planet2"], str) else trine2["planet2"]
                    
                    if trine2_p1 in [planet1, planet2] or trine2_p2 in [planet1, planet2]:
                        for k, trine3 in enumerate(trines):
                            if k != i and k != j:
                                trine3_p1 = trine3["planet1"].lower() if isinstance(trine3["planet1"], str) else trine3["planet1"]
                                trine3_p2 = trine3["planet2"].lower() if isinstance(trine3["planet2"], str) else trine3["planet2"]
                                
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
        
        # Group aspects by type, normalize numeric aspect types
        squares = []
        oppositions = []
        
        for aspect in aspects:
            aspect_type = aspect.get("type")
            # Handle numeric or string representation
            if aspect_type in [90, "90", "square"]:
                squares.append(aspect)
            elif aspect_type in [180, "180", "opposition"]:
                oppositions.append(aspect)
        
        # Check each opposition for potential T-square
        for opp in oppositions:
            planet1 = opp["planet1"].lower() if isinstance(opp["planet1"], str) else opp["planet1"]
            planet2 = opp["planet2"].lower() if isinstance(opp["planet2"], str) else opp["planet2"]
            
            # Look for squares to both planets in opposition
            for sq1 in squares:
                sq_planet1 = sq1["planet1"].lower() if isinstance(sq1["planet1"], str) else sq1["planet1"]
                sq_planet2 = sq1["planet2"].lower() if isinstance(sq1["planet2"], str) else sq1["planet2"]
                
                # Check if this square connects to one opposition planet
                if sq_planet1 in [planet1, planet2] or sq_planet2 in [planet1, planet2]:
                    # Get the planet that forms the apex (square to both opposition planets)
                    apex_planet = sq_planet1 if sq_planet1 not in [planet1, planet2] else sq_planet2
                    base_planets = [planet1, planet2]
                    
                    # Look for second square to complete the T-square
                    for sq2 in squares:
                        if sq2 != sq1:  # Different square
                            sq2_planet1 = sq2["planet1"].lower() if isinstance(sq2["planet1"], str) else sq2["planet1"]
                            sq2_planet2 = sq2["planet2"].lower() if isinstance(sq2["planet2"], str) else sq2["planet2"]
                            
                            # Check if this square connects apex to the other opposition planet
                            if (sq2_planet1 == apex_planet and sq2_planet2 in base_planets) or \
                               (sq2_planet2 == apex_planet and sq2_planet1 in base_planets):
                                # Create the T-square
                                planets = [planet1, planet2, apex_planet]
                                
                                # Create a unique key for this combination
                                key = "-".join(sorted(planets))
                                if key not in seen_combinations:
                                    seen_combinations.add(key)
                                    t_squares.append({
                                        "planets": planets,
                                        "apex": apex_planet
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

    def _get_planet_dignity(self, planet: str, sign_or_birth_chart=None, house=None) -> Dict[str, Any]:
        """Get dignity information for a planet."""
        result = {
            "planet": planet,
            "dignity": "neutral",
            "score": 0
        }
        
        # Handle case where sign_or_birth_chart is a birth chart
        if isinstance(sign_or_birth_chart, dict) and "planets" in sign_or_birth_chart:
            if planet in sign_or_birth_chart["planets"]:
                planet_data = sign_or_birth_chart["planets"][planet]
                sign = planet_data.get("sign", "")
                house = planet_data.get("house", house)
            else:
                self.logger.warning(f"Planet {planet} not found in birth chart")
                return result
        else:
            sign = sign_or_birth_chart
        
        try:
            # Get essential dignity (based on planet's sign placement)
            if sign:
                essential_dignity = self._get_essential_dignity(planet, sign)
                result["essential_dignity"] = essential_dignity
                
                # Add a score based on essential dignity
                dignity_scores = {
                    "rulership": 5,
                    "exaltation": 4,
                    "triplicity": 3,
                    "term": 2,
                    "face": 1,
                    "detriment": -5,
                    "fall": -4,
                    "peregrine": -1,
                    "neutral": 0
                }
                result["essential_score"] = dignity_scores.get(essential_dignity, 0)
                result["score"] += result["essential_score"]
            
            # Get accidental dignity (based on planet's house placement)
            if house:
                accidental_dignity = self._get_accidental_dignity(planet, house)
                result["accidental_dignity"] = accidental_dignity
                
                # Add a score based on accidental dignity
                house_scores = {
                    "angular": 4,
                    "succedent": 2,
                    "cadent": 0,
                    "joy": 3,
                    "detriment": -3,
                    "neutral": 0
                }
                result["accidental_score"] = house_scores.get(accidental_dignity, 0)
                result["score"] += result["accidental_score"]
            
            # Determine overall dignity
            if result["score"] >= 5:
                result["dignity"] = "very dignified"
            elif result["score"] >= 2:
                result["dignity"] = "dignified"
            elif result["score"] <= -5:
                result["dignity"] = "very debilitated"
            elif result["score"] <= -2:
                result["dignity"] = "debilitated"
            else:
                result["dignity"] = "neutral"
                
        except Exception as e:
            self.logger.error(f"Error calculating planet dignity: {str(e)}")
            
        return result

    def _get_accidental_dignity(self, planet: str, house: str) -> str:
        """Determine a planet's accidental dignity based on house placement.
        
        Args:
            planet: The planet name
            house: The house number (as a string)
            
        Returns:
            String representing accidental dignity ("joy", "strong", "neutral", "weak", "very_weak")
        """
        # House joys (where planets are happiest)
        house_joys = {
            "mercury": "1",  # Some traditions use 3rd house
            "moon": "3",
            "venus": "5",
            "mars": "6",
            "sun": "9",
            "jupiter": "11",
            "saturn": "12"
        }
        
        # Houses where planets are strong
        strong_houses = {
            "sun": ["1", "5", "9"],
            "moon": ["3", "4", "7"],
            "mercury": ["1", "3", "6"],
            "venus": ["2", "5", "7"],
            "mars": ["1", "5", "8"],
            "jupiter": ["2", "9", "11"],
            "saturn": ["4", "10", "11"],
            "uranus": ["1", "4", "11"],
            "neptune": ["4", "9", "12"],
            "pluto": ["1", "8", "12"],
            "north_node": ["3", "9", "11"],
            "south_node": ["3", "9", "11"],
            "chiron": ["6", "9", "12"]
        }
        
        # Houses where planets are weak
        weak_houses = {
            "sun": ["2", "8", "12"],
            "moon": ["1", "8", "12"],
            "mercury": ["8", "9", "12"],
            "venus": ["6", "8", "12"],
            "mars": ["2", "7", "12"],
            "jupiter": ["6", "8", "12"],
            "saturn": ["1", "5", "7"],
            "uranus": ["2", "6", "8"],
            "neptune": ["1", "2", "6"],
            "pluto": ["2", "6", "9"],
            "north_node": ["4", "6", "8"],
            "south_node": ["4", "6", "8"],
            "chiron": ["1", "4", "8"]
        }
        
        normalized_planet = planet.lower()
        
        # Check for house joy
        if normalized_planet in house_joys and house_joys[normalized_planet] == house:
            return "joy"
        
        # Check for strong house
        if normalized_planet in strong_houses and house in strong_houses[normalized_planet]:
            return "strong"
        
        # Check for weak house
        if normalized_planet in weak_houses and house in weak_houses[normalized_planet]:
            return "weak"
        
        # Check for cadent houses, which are generally less favorable
        if house in ["3", "6", "9", "12"]:
            return "weak"
        
        # Houses 8 and 12 are traditionally the most challenging
        if house in ["8", "12"]:
            return "very_weak"
        
        return "neutral"

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

    def _analyze_combinations(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze important planetary combinations in the birth chart."""
        try:
            combinations = {}
            planets = birth_chart.get("planets", {})
            
            # Analyze Sun-Moon combination
            if "sun" in planets and "moon" in planets:
                sun_sign = planets["sun"].get("sign")
                moon_sign = planets["moon"].get("sign")
                if sun_sign and moon_sign:
                    sun_element = self.structured_data.get("signs", {}).get(sun_sign.lower(), {}).get("element")
                    moon_element = self.structured_data.get("signs", {}).get(moon_sign.lower(), {}).get("element")
                    
                    if sun_element == moon_element:
                        combo_type = "same_element"
                    elif (sun_element in ["fire", "air"] and moon_element in ["fire", "air"]) or \
                         (sun_element in ["earth", "water"] and moon_element in ["earth", "water"]):
                        combo_type = "compatible_elements"
                    else:
                        combo_type = "incompatible_elements"
                    
                    combinations["sun_moon"] = {
                        "type": combo_type,
                        "interpretation": self.structured_data.get("interpretation_combinations", {})
                                        .get("sun_moon_combinations", {})
                                        .get(combo_type, {})
                                        .get("interpretation", "")
                    }
            
            return combinations
        except Exception as e:
            self.logger.error(f"Error analyzing combinations: {str(e)}")
            return {}

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
        """Generate interpretation for a stellium pattern."""
        pattern_data = self.structured_data.get("interpretation_patterns", {})
        sign_data = self.structured_data.get("signs", {}).get(sign.lower(), {})
        
        planet_list = ", ".join(planets)
        qualities = sign_data.get("keywords", [])
        focus = sign_data.get("focus", "")
        element = sign_data.get("element", "")
        modality = sign_data.get("modality", "")
        
        # Get element influence
        element_influence = ""
        elemental_patterns = pattern_data.get("elemental_patterns", {})
        if element and f"{element}_dominant" in elemental_patterns:
            element_data = elemental_patterns[f"{element}_dominant"]
            strengths = ", ".join(element_data.get("strengths", []))
            element_influence = f" The {element} element gives strengths in {strengths}."
        
        # Get modality influence
        modality_influence = ""
        modality_patterns = pattern_data.get("modality_patterns", {})
        if modality and f"{modality}_dominant" in modality_patterns:
            modality_data = modality_patterns[f"{modality}_dominant"]
            modality_desc = modality_data.get("description", "")
            modality_influence = f" {modality_desc}"
        
        return f"Stellium in {sign} with {planet_list}. This concentration of energy in {sign} indicates a strong focus on {', '.join(qualities)}. {focus}{element_influence}{modality_influence}"
    
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
        """Generate interpretations for aspects between planets."""
        try:
            # Normalize inputs to prevent case issues
            normalized_planet1 = planet1.lower()
            normalized_planet2 = planet2.lower()
            
            # Convert aspect_type to string if it's an integer (angle value)
            if isinstance(aspect_type, int):
                aspect_type = str(aspect_type)
            
            # Get the base interpretation for the aspect
            base_interpretation = self._get_base_aspect_interpretation(normalized_planet1, normalized_planet2, aspect_type)
            
            if not base_interpretation:
                self.logger.debug(f"No base interpretation found for {normalized_planet1}-{normalized_planet2} {aspect_type} aspect")
                # Try the reverse order of planets as a fallback
                base_interpretation = self._get_base_aspect_interpretation(normalized_planet2, normalized_planet1, aspect_type)
                
                if not base_interpretation:
                    # If we still don't have a base interpretation, try to generate a basic one
                    aspects_data = self.structured_data.get("aspects", {})
                    aspect_info = aspects_data.get(aspect_type, {})
                    aspect_name = aspect_info.get("name", aspect_type)
                    
                    planets_data = self.structured_data.get("planets", {})
                    planet1_info = planets_data.get(normalized_planet1, {})
                    planet2_info = planets_data.get(normalized_planet2, {})
                    
                    planet1_keywords = planet1_info.get("keywords", [])
                    planet2_keywords = planet2_info.get("keywords", [])
                    
                    planet1_keyword = planet1_keywords[0] if planet1_keywords else normalized_planet1
                    planet2_keyword = planet2_keywords[0] if planet2_keywords else normalized_planet2
                    
                    aspect_keywords = aspect_info.get("keywords", [])
                    aspect_keyword = aspect_keywords[0] if aspect_keywords else "interacts with"
                    
                    base_interpretation = f"Your {normalized_planet1} ({planet1_keyword}) {aspect_keyword} your {normalized_planet2} ({planet2_keyword})."
            
            # Get the pattern context for additional dimension
            pattern_context = self._get_pattern_context(normalized_planet1, normalized_planet2, aspect_type, birth_chart)
            
            # Check if either planet is retrograde
            retrograde_influence = self._get_retrograde_influence(normalized_planet1, normalized_planet2, birth_chart)
            
            # Get house context interpretation
            house_context = self._get_house_context_interpretation(normalized_planet1, normalized_planet2, birth_chart)
            
            # Combine the parts
            parts = [base_interpretation]
            
            if pattern_context and level != "basic":
                parts.append(pattern_context)
                
            if retrograde_influence and level != "basic":
                parts.append(retrograde_influence)
                
            if house_context and level != "basic":
                parts.append(house_context)
                
            # Consider the orb strength in the interpretation
            orb_strength = self._calculate_orb_strength(orb, aspect_type)
            
            # Add orb strength interpretation for detailed levels
            if level != "basic" and orb_strength is not None:
                if orb_strength > 0.8:
                    parts.append("This aspect is very strong with a tight orb, making its influence particularly noticeable in your chart.")
                elif orb_strength < 0.4:
                    parts.append("With a wide orb, this aspect's influence is more subtle in your chart.")
            
            # Join all parts into a unified interpretation
            return " ".join(parts)

        except Exception as e:
            self.logger.error(f"Error generating aspect interpretation: {str(e)}")
            return f"Aspect between {planet1} and {planet2}."

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
        """Get additional context for aspect pattern interpretation based on house placements."""
        try:
            context_parts = []
            
            # Get house placements
            planet1_house = birth_chart.get("planets", {}).get(planet1, {}).get("house")
            planet2_house = birth_chart.get("planets", {}).get(planet2, {}).get("house")
            
            if planet1_house and planet2_house:
                # Get house information
                house1_info = self.structured_data.get("houses", {}).get(str(planet1_house), {})
                house2_info = self.structured_data.get("houses", {}).get(str(planet2_house), {})
                
                # Add house context
                if house1_info and house2_info:
                    house1_name = house1_info.get("name", f"House {planet1_house}")
                    house2_name = house2_info.get("name", f"House {planet2_house}")
                    
                    context_parts.append(f"This aspect connects your {house1_name} ({planet1_house}) with your {house2_name} ({planet2_house})")
            
            # Format the result
            if context_parts:
                return " ".join(context_parts)
            else:
                return ""
            
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
        """Analyze the elemental balance of the birth chart."""
        try:
            # Initialize element counts
            elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
            planets_by_element = {"fire": [], "earth": [], "air": [], "water": []}
            
            # Count planets in each element
            for planet, data in birth_chart.get("planets", {}).items():
                sign = data.get("sign", "").lower()
                if sign:
                    sign_data = self.structured_data.get("signs", {}).get(sign, {})
                    element = sign_data.get("element")
                    if element:
                        elements[element] += 1
                        planets_by_element[element].append(planet)
            
            # Calculate percentages
            total_planets = sum(elements.values())
            percentages = {}
            for element, count in elements.items():
                if total_planets > 0:
                    percentages[element] = (count / total_planets) * 100
                else:
                    percentages[element] = 0
            
            # Determine dominant and lacking elements
            dominant_elements = [e for e, count in elements.items() if count >= 3]
            lacking_elements = [e for e, count in elements.items() if count == 0]
            
            return {
                "elements": elements,
                "planets_by_element": planets_by_element,
                "percentages": percentages,
                "dominant_elements": dominant_elements,
                "lacking_elements": lacking_elements
            }
        except Exception as e:
            self.logger.error(f"Error analyzing element balance: {str(e)}")
            return {}

    def _analyze_simple_modality_balance(self, birth_chart: Dict) -> Dict[str, Any]:
        """Analyze the modality balance of the birth chart."""
        try:
            # Initialize modality counts
            modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
            planets_by_modality = {"cardinal": [], "fixed": [], "mutable": []}
            
            # Count planets in each modality
            for planet, data in birth_chart.get("planets", {}).items():
                sign = data.get("sign", "").lower()
                if sign:
                    sign_data = self.structured_data.get("signs", {}).get(sign, {})
                    modality = sign_data.get("modality")
                    if modality:
                        modalities[modality] += 1
                        planets_by_modality[modality].append(planet)
            
            # Calculate percentages
            total_planets = sum(modalities.values())
            percentages = {}
            for modality, count in modalities.items():
                if total_planets > 0:
                    percentages[modality] = (count / total_planets) * 100
                else:
                    percentages[modality] = 0
            
            # Determine dominant and lacking modalities
            dominant_modalities = [m for m, count in modalities.items() if count >= 3]
            lacking_modalities = [m for m, count in modalities.items() if count == 0]
            
            return {
                "modalities": modalities,
                "planets_by_modality": planets_by_modality,
                "percentages": percentages,
                "dominant_modalities": dominant_modalities,
                "lacking_modalities": lacking_modalities
            }
        except Exception as e:
            self.logger.error(f"Error analyzing modality balance: {str(e)}")
            return {}

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

    def _analyze_simple_patterns(self, birth_chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze the birth chart for simple patterns like stelliums.
        
        Args:
            birth_chart: Dictionary containing birth chart data
            
        Returns:
            List of dictionaries containing pattern information
        """
        self.logger.debug("Analyzing simple patterns")
        patterns = []
        
        try:
            planets_by_sign = {}
            planets_by_element = {}
            planets_by_modality = {}
            
            # Group planets by sign
            for planet_name, planet_data in birth_chart.get("planets", {}).items():
                sign = planet_data.get("sign", "Unknown")
                if sign == "Unknown":
                    continue
                
                # Skip angles or other non-traditional planets if needed
                if planet_name in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                    continue
                
                # Add to sign grouping
                if sign not in planets_by_sign:
                    planets_by_sign[sign] = []
                planets_by_sign[sign].append(planet_name)
                
                # Get element and modality
                normalized_sign = sign.lower()
                if normalized_sign in self._sign_cache:
                    element = self._sign_cache[normalized_sign].get("element", "")
                    modality = self._sign_cache[normalized_sign].get("modality", "")
                    
                    if element:
                        if element not in planets_by_element:
                            planets_by_element[element] = []
                        planets_by_element[element].append(planet_name)
                    
                    if modality:
                        if modality not in planets_by_modality:
                            planets_by_modality[modality] = []
                        planets_by_modality[modality].append(planet_name)
            
            # Check for stelliums (3+ planets in same sign)
            for sign, planets in planets_by_sign.items():
                if len(planets) >= 3:
                    # Generate stellium interpretation
                    interpretation = self._get_stellium_interpretation(sign, planets)
                    patterns.append({
                        "type": "stellium",
                        "sign": sign,
                        "planets": planets,
                        "interpretation": interpretation
                    })
            
            # Check for element emphasis (4+ planets in same element)
            for element, planets in planets_by_element.items():
                if len(planets) >= 4:
                    patterns.append({
                        "type": "element_emphasis",
                        "element": element,
                        "planets": planets,
                        "interpretation": f"Emphasis on {element} element with planets: {', '.join(planets)}. This indicates a strong focus on {self._get_element_modality_qualities_simple(element, '')}."
                    })
            
            # Check for modality emphasis (4+ planets in same modality)
            for modality, planets in planets_by_modality.items():
                if len(planets) >= 4:
                    patterns.append({
                        "type": "modality_emphasis",
                        "modality": modality,
                        "planets": planets,
                        "interpretation": f"Emphasis on {modality} modality with planets: {', '.join(planets)}. This indicates a strong focus on {self._get_element_modality_qualities_simple('', modality)}."
                    })
        
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {str(e)}")
        
        return patterns

    def _get_stellium_interpretation(self, sign: str, planets: List[str]) -> str:
        """Generate interpretation for a stellium pattern."""
        pattern_data = self.structured_data.get("interpretation_patterns", {})
        sign_data = self.structured_data.get("signs", {}).get(sign.lower(), {})
        
        planet_list = ", ".join(planets)
        qualities = sign_data.get("keywords", [])
        focus = sign_data.get("focus", "")
        element = sign_data.get("element", "")
        modality = sign_data.get("modality", "")
        
        # Get element influence
        element_influence = ""
        elemental_patterns = pattern_data.get("elemental_patterns", {})
        if element and f"{element}_dominant" in elemental_patterns:
            element_data = elemental_patterns[f"{element}_dominant"]
            strengths = ", ".join(element_data.get("strengths", []))
            element_influence = f" The {element} element gives strengths in {strengths}."
        
        # Get modality influence
        modality_influence = ""
        modality_patterns = pattern_data.get("modality_patterns", {})
        if modality and f"{modality}_dominant" in modality_patterns:
            modality_data = modality_patterns[f"{modality}_dominant"]
            modality_desc = modality_data.get("description", "")
            modality_influence = f" {modality_desc}"
        
        return f"Stellium in {sign} with {planet_list}. This concentration of energy in {sign} indicates a strong focus on {', '.join(qualities)}. {focus}{element_influence}{modality_influence}"

    def _find_yod(self, aspects: List[Dict[str, Any]]) -> List[List[str]]:
        """Find Yod patterns in the aspects.
        
        Args:
            aspects: List of aspects in the birth chart
            
        Returns:
            List of lists containing Yod pattern information
        """
        yods = []
        seen_combinations = set()
        
        # Group aspects by type
        sextiles = [a for a in aspects if str(a["type"]) == "60"]
        squares = [a for a in aspects if str(a["type"]) == "90"]
        oppositions = [a for a in aspects if str(a["type"]) == "180"]
        
        # Check each sextile for potential Yod
        for sextile in sextiles:
            planet1 = sextile["planet1"].lower()
            planet2 = sextile["planet2"].lower()
            
            # Look for squares to both planets
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
                                        yods.append(planets)
        
        return yods

    def _get_essential_dignity(self, planet: str, sign: str) -> str:
        """Determine essential dignity of a planet in a sign."""
        
        # Normalize inputs
        planet = planet.lower()
        sign = sign.lower()
        
        # Rule dictionaries for essential dignity
        rulership = {
            "sun": "leo",
            "moon": "cancer",
            "mercury": ["gemini", "virgo"],
            "venus": ["taurus", "libra"],
            "mars": ["aries", "scorpio"],
            "jupiter": ["sagittarius", "pisces"],
            "saturn": ["capricorn", "aquarius"],
            "uranus": "aquarius",  # Modern rulership
            "neptune": "pisces",   # Modern rulership
            "pluto": "scorpio"     # Modern rulership
        }
        
        exaltation = {
            "sun": "aries",
            "moon": "taurus",
            "mercury": "virgo",
            "venus": "pisces",
            "mars": "capricorn",
            "jupiter": "cancer",
            "saturn": "libra",
            "uranus": "scorpio",   # Modern concept
            "neptune": "leo",      # Modern concept
            "pluto": "aquarius"    # Modern concept
        }
        
        detriment = {
            "sun": "aquarius",
            "moon": "capricorn",
            "mercury": ["sagittarius", "pisces"],
            "venus": ["aries", "scorpio"],
            "mars": ["libra", "taurus"],
            "jupiter": ["gemini", "virgo"],
            "saturn": ["cancer", "leo"],
            "uranus": "leo",       # Modern concept
            "neptune": "virgo",    # Modern concept
            "pluto": "taurus"      # Modern concept
        }
        
        fall = {
            "sun": "libra",
            "moon": "scorpio",
            "mercury": "pisces",
            "venus": "virgo",
            "mars": "cancer",
            "jupiter": "capricorn",
            "saturn": "aries",
            "uranus": "taurus",    # Modern concept
            "neptune": "aquarius", # Modern concept
            "pluto": "leo"         # Modern concept
        }
        
        # Check rulership (strongest dignity)
        if sign in rulership.get(planet, []) if isinstance(rulership.get(planet), list) else sign == rulership.get(planet):
            return "rulership"
            
        # Check exaltation
        if sign == exaltation.get(planet):
            return "exaltation"
            
        # Check detriment
        if sign in detriment.get(planet, []) if isinstance(detriment.get(planet), list) else sign == detriment.get(planet):
            return "detriment"
            
        # Check fall
        if sign == fall.get(planet):
            return "fall"
            
        # If none of the above, the planet is peregrine
        return "peregrine"

    def _get_sign_index(self, sign: str) -> int:
        """Get the index of a sign in the zodiac.
        
        Args:
            sign: Sign name
            
        Returns:
            Index (0-11) of the sign
        """
        signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", 
                "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
        
        sign = sign.lower()
        if sign in signs:
            return signs.index(sign)
        return 0
    
    def _get_sign_from_index(self, index: int) -> str:
        """Get the sign name from an index.
        
        Args:
            index: Index (0-11) of the sign
            
        Returns:
            Sign name in lowercase
        """
        signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", 
                "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
        
        return signs[index % 12]

    def _get_compatibility_interpretation(self, planet1: str, planet2: str) -> str:
        """Generate an interpretation of the compatibility between two planets."""
        # Normalize planet names
        planet1 = planet1.lower()
        planet2 = planet2.lower()
        
        # These pairs represent classic harmonic relationships in astrology
        harmonious_pairs = [
            # Same element pairs
            {"planets": ["sun", "mars"], "reason": "both fiery and active"},
            {"planets": ["sun", "jupiter"], "reason": "both expansive and warm"},
            {"planets": ["moon", "venus"], "reason": "both receptive and nurturing"},
            {"planets": ["moon", "neptune"], "reason": "both intuitive and sensitive"},
            {"planets": ["mercury", "uranus"], "reason": "both intellectual and quick-thinking"},
            {"planets": ["venus", "neptune"], "reason": "both romantic and idealistic"},
            {"planets": ["mars", "pluto"], "reason": "both powerful and transformative"},
            {"planets": ["jupiter", "sun"], "reason": "both optimistic and growth-oriented"},
            {"planets": ["saturn", "mercury"], "reason": "both structured and detail-oriented"},
            {"planets": ["uranus", "mercury"], "reason": "both inventive and forward-thinking"},
            {"planets": ["neptune", "moon"], "reason": "both dreamy and empathic"},
            {"planets": ["pluto", "mars"], "reason": "both intense and focused"}
        ]
        
        # These pairs represent classic challenging relationships in astrology
        challenging_pairs = [
            {"planets": ["sun", "saturn"], "reason": "sun's expression can be limited by saturn's restrictions"},
            {"planets": ["moon", "mars"], "reason": "emotional sensitivity meets directness and aggression"},
            {"planets": ["mercury", "neptune"], "reason": "logical thinking clashes with dreaminess and confusion"},
            {"planets": ["venus", "pluto"], "reason": "harmony confronts intensity and control"},
            {"planets": ["mars", "saturn"], "reason": "action and drive meet limitation and delay"},
            {"planets": ["jupiter", "mercury"], "reason": "expansion conflicts with detailed analysis"},
            {"planets": ["saturn", "jupiter"], "reason": "restriction versus expansion creates tension"},
            {"planets": ["uranus", "venus"], "reason": "unpredictability challenges relationship harmony"},
            {"planets": ["neptune", "mercury"], "reason": "confusion disrupts clear communication"},
            {"planets": ["pluto", "sun"], "reason": "power struggles with self-expression"}
        ]
        
        # Check if our planets are in a harmonious pair
        for pair in harmonious_pairs:
            if (planet1 in pair["planets"] and planet2 in pair["planets"]):
                return f"These planets work well together, being {pair['reason']}."
                
        # Check if our planets are in a challenging pair
        for pair in challenging_pairs:
            if (planet1 in pair["planets"] and planet2 in pair["planets"]):
                return f"These planets can create tension, as {pair['reason']}."
        
        # For pairs not in our predefined lists, return a generic statement
        # based on traditional planetary qualities
        planetary_qualities = {
            "sun": {"element": "fire", "modality": "fixed", "nature": "warm, creative, expressive"},
            "moon": {"element": "water", "modality": "cardinal", "nature": "emotional, nurturing, responsive"},
            "mercury": {"element": "air", "modality": "mutable", "nature": "communicative, analytical, adaptable"},
            "venus": {"element": "earth/air", "modality": "fixed/cardinal", "nature": "harmonious, relational, artistic"},
            "mars": {"element": "fire", "modality": "cardinal", "nature": "active, assertive, energetic"},
            "jupiter": {"element": "fire", "modality": "mutable", "nature": "expansive, optimistic, growth-oriented"},
            "saturn": {"element": "earth", "modality": "cardinal", "nature": "structured, responsible, limiting"},
            "uranus": {"element": "air", "modality": "fixed", "nature": "innovative, unpredictable, freedom-seeking"},
            "neptune": {"element": "water", "modality": "mutable", "nature": "dreamy, spiritual, dissolving"},
            "pluto": {"element": "water", "modality": "fixed", "nature": "transformative, intense, powerful"}
        }
        
        # If both planets have defined qualities
        if planet1 in planetary_qualities and planet2 in planetary_qualities:
            p1_qualities = planetary_qualities[planet1]
            p2_qualities = planetary_qualities[planet2]
            
            # Determine compatibility based on elements
            element_compatibility = ""
            if p1_qualities["element"] == p2_qualities["element"]:
                element_compatibility = f"Both planets share the {p1_qualities['element']} element, creating natural harmony."
            elif (p1_qualities["element"] == "fire" and p2_qualities["element"] == "air") or \
                 (p1_qualities["element"] == "air" and p2_qualities["element"] == "fire"):
                element_compatibility = "Fire and air elements complement each other, creating stimulation and inspiration."
            elif (p1_qualities["element"] == "earth" and p2_qualities["element"] == "water") or \
                 (p1_qualities["element"] == "water" and p2_qualities["element"] == "earth"):
                element_compatibility = "Earth and water elements work well together, creating nurturing and stability."
            else:
                # For other element combinations, we'll skip element compatibility
                pass
            
            # Create a general interpretation
            return f"{planet1.capitalize()} ({p1_qualities['nature']}) interacts with {planet2.capitalize()} ({p2_qualities['nature']}). {element_compatibility}"
        
        # Default return for unlisted planetary pairs
        return ""