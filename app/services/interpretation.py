"""Astrological interpretation service module."""

# Standard library imports
from datetime import datetime
import json
import logging
import os
from typing import Dict, Any, List, Tuple

# Third-party imports
from flatlib.datetime import Datetime

# Local application imports
from app.services.birth_chart import BirthChartService
from app.services.chart_statistics import ChartStatisticsService

logger = logging.getLogger(__name__)


class InterpretationService:
    """Astrological interpretation service that generates detailed birth chart analyses.

    This service provides methods for analyzing birth charts, detecting astrological patterns,
    and generating interpretations based on planetary positions, house placements,
    aspects, and other astrological factors.
    """

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
                    "personal_growth": "identity and self-expression",
                }
            },
            "moon": {
                "qualities": {
                    "general": "emotions and instincts",
                    "career": "emotional satisfaction",
                    "relationships": "emotional needs",
                    "health": "emotional well-being",
                    "spirituality": "intuition and receptivity",
                    "personal_growth": "emotional awareness",
                }
            },
        }

        self.houses_data = {
            "1": {
                "qualities": {
                    "general": "self-expression and personality",
                    "career": "leadership style",
                    "relationships": "approach to relationships",
                    "health": "physical vitality",
                    "spirituality": "spiritual identity",
                    "personal_growth": "self-awareness",
                }
            },
            "10": {
                "qualities": {
                    "general": "career and public image",
                    "career": "professional goals",
                    "relationships": "public partnerships",
                    "health": "public health",
                    "spirituality": "spiritual authority",
                    "personal_growth": "life purpose",
                }
            },
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
                    "personal_growth": "self-assertion",
                },
                "compatible_signs": ["Leo", "Sagittarius", "Gemini", "Libra"],
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
                    "personal_growth": "self-discipline",
                },
                "compatible_signs": ["Taurus", "Virgo", "Scorpio", "Pisces"],
            },
        }

    def _load_structured_data(self):
        """Load structured data from JSON files."""
        try:
            # Define path to structured data directory
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "structured",
            )

            # Load each JSON file into structured_data dictionary
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(data_dir, filename)
                    key = filename.replace(".json", "")

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            self.structured_data[key] = json.load(f)
                            self.logger.debug(f"Successfully loaded {filename}")
                    except Exception as e:
                        self.logger.error(f"Error loading {filename}: {str(e)}")

            # Convert numeric aspect types to strings for consistency - using a copy to avoid mutation during iteration
            aspect_data = self.structured_data.get("aspects", {})
            aspect_types_to_add = {}

            for key, data in list(aspect_data.items()):
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
                self.logger.debug(
                    f"Available signs in descriptions: {list(self.structured_data['descriptions'].keys())}"
                )
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
                self._planet_cache = dict((k.lower(), v) for k, v in planets_data.items())

            # Initialize sign cache
            signs_data = self.structured_data.get("signs", {})
            if signs_data:
                self._sign_cache = dict((k.lower(), v) for k, v in signs_data.items())

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

            for key, data in list(self._aspect_cache.items()):
                if "angle" in data:
                    angle_str = str(data["angle"])
                    # Use the key in logging to avoid the unused variable warning
                    self.logger.debug(f"Converting aspect type {key} to numeric key {angle_str}")
                    aspect_types_to_add[angle_str] = data

            # Add the new aspect types separately
            for angle_str, data in aspect_types_to_add.items():
                if angle_str not in self._aspect_cache:
                    self._aspect_cache[angle_str] = data

            self.logger.debug("Successfully initialized caches")
        except Exception as e:
            self.logger.error(f"Error initializing caches: {str(e)}", exc_info=True)

    def _load_sun_qualities(self):
        """Load sun sign qualities into the cache.

        This method extracts qualities from the structured data and prepares
        them for use in interpretations.
        """
        try:
            # Try to get sun sign qualities from structured data
            signs_data = self.structured_data.get("signs", {})
            if not signs_data:
                self.logger.debug("No signs data found for sun qualities")
                return

            # Process each sign and extract qualities
            for sign, data in signs_data.items():
                if "qualities" in data:
                    sign_key = sign.lower()
                    if sign_key not in self._sign_cache:
                        self._sign_cache[sign_key] = {}
                    self._sign_cache[sign_key]["qualities"] = data["qualities"]

            self.logger.debug("Successfully loaded sun qualities")
        except Exception as e:
            self.logger.error(f"Error loading sun qualities: {str(e)}")

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
        """Validate birth chart data structure.

        Args:
            birth_chart: Birth chart data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic structure checks
        if not isinstance(birth_chart, dict):
            self.logger.error("Birth chart must be a dictionary")
            return False

        # Check for planets
        if "planets" not in birth_chart:
            self.logger.error("Birth chart must contain planets")
            return False

        # Check planets are a list for new format
        planets = birth_chart.get("planets", [])
        if not isinstance(planets, list):
            self.logger.error("Planets must be a list")
            return False

        # Check each planet has required fields
        for planet in planets:
            if not isinstance(planet, dict):
                self.logger.error("Each planet must be a dictionary")
                return False

            if "name" not in planet:
                self.logger.error("Each planet must have a name")
                return False

            if "sign" not in planet:
                self.logger.error("Each planet must have a sign")
                return False

        # Check for houses (optional but recommended)
        houses = birth_chart.get("houses", [])
        if houses and not isinstance(houses, list):
            self.logger.error("Houses must be a list")
            return False

        # Check each house has required fields
        for house in houses:
            if not isinstance(house, dict):
                self.logger.error("Each house must be a dictionary")
                return False

            if "house_num" not in house:
                self.logger.error("Each house must have a house_num")
                return False

            if "sign" not in house:
                self.logger.error("Each house must have a sign")
                return False

        # Check for aspects (optional but recommended)
        aspects = birth_chart.get("aspects", [])
        if aspects and not isinstance(aspects, list):
            self.logger.error("Aspects must be a list")
            return False

        # All checks passed
        return True

    def _validate_interpretation_request(self, request: Dict) -> Tuple[bool, str]:
        """Validate the interpretation request.

        Args:
            request: The interpretation request to validate

        Returns:
            A tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            if not request.get("birth_chart") and not all(
                request.get(field) for field in ["date_of_birth", "latitude", "longitude"]
            ):
                return (
                    False,
                    "Either birth_chart or date_of_birth, latitude, and longitude must be provided",
                )

            # Validate date_of_birth if provided
            if request.get("date_of_birth"):
                try:
                    datetime.fromisoformat(request["date_of_birth"].replace("Z", "+00:00"))
                except ValueError:
                    return (
                        False,
                        "Invalid date_of_birth format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
                    )

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
                return (
                    False,
                    "Invalid interpretation level. Must be 'basic' or 'detailed'",
                )

            # Validate area
            valid_areas = [
                "general",
                "career",
                "relationships",
                "health",
                "spirituality",
                "personal_growth",
            ]
            if request.get("area") not in valid_areas + [None]:
                return (
                    False,
                    f"Invalid interpretation area. Must be one of: {', '.join(valid_areas)}",
                )

            return True, ""

        except Exception as e:
            logger.error(f"Error validating interpretation request: {str(e)}", exc_info=True)
            return False, str(e)

    def generate_interpretation(
        self, birth_chart: Dict[str, Any], level: str = "basic", area: str = "general"
    ) -> Dict[str, Any]:
        """Generate an interpretation for a birth chart.

        Args:
            birth_chart: Birth chart data to interpret
            level: Level of detail for the interpretation (basic, intermediate, detailed)
            area: Area of life to focus on for the interpretation (general, career, love, etc.)

        Returns:
            Dictionary containing the interpretation
        """
        self.logger.info(f"Generating interpretation (level: {level}, area: {area})")

        # Validate the birth chart
        if not self._validate_birth_chart(birth_chart):
            self.logger.error("Invalid birth chart data")
            return {"error": "Invalid birth chart data"}

        # Store the birth chart in the service instance
        self.birth_chart = birth_chart

        # Use the new interpretation method
        interpretation = self.interpret_birth_chart()

        # Add additional analysis based on level and area
        if level == "detailed":
            # Add element and modality balance
            element_balance = self._analyze_simple_element_balance(birth_chart)
            modality_balance = self._analyze_simple_modality_balance(birth_chart)

            interpretation["element_balance"] = element_balance
            interpretation["modality_balance"] = modality_balance

            # Add combinations analysis
            interpretation["combinations"] = self._analyze_combinations(birth_chart)

            # Add summary based on rising sign
            rising_sign = None
            for planet in birth_chart.get("planets", []):
                if planet.get("name", "").lower() == "ascendant":
                    rising_sign = planet.get("sign")
                    break

            if rising_sign:
                interpretation["summary"] = self._get_rising_sign_summary(rising_sign)

        return interpretation

    def _get_house_interpretations(self) -> List[Dict[str, Any]]:
        """Generate interpretations for houses in the birth chart.

        Returns:
            List of dictionaries containing house interpretations
        """
        house_interpretations = []

        # Loop through the houses (1-12)
        for house_num in range(1, 13):
            # Get the sign on the cusp of the house
            house_data = next(
                (h for h in self.birth_chart.get("houses", []) if h.get("house_num") == house_num),
                None,
            )

            if not house_data:
                continue

            sign = house_data.get("sign")
            if not sign:
                continue

            # Get planets in this house
            planets_in_house = []
            for planet in self.birth_chart.get("planets", []):
                if planet.get("house") == house_num:
                    planets_in_house.append(planet.get("name"))

            # Get the interpretation for this house
            interpretation = self._get_house_interpretation(str(house_num), sign)

            # Create the house interpretation object
            house_interp = {
                "house": house_num,
                "sign": sign,
                "planets": planets_in_house,
                "interpretation": interpretation,
            }

            house_interpretations.append(house_interp)

        return house_interpretations

    def _get_house_interpretation(self, house: str, sign: str) -> str:
        """Get the interpretation for a house in a particular sign.

        Args:
            house: House number as a string
            sign: Sign on the cusp of the house

        Returns:
            String containing the house interpretation
        """
        # Try to get from structured data first
        houses_data = self.structured_data.get("houses", {})
        sign_data = houses_data.get(house, {}).get(sign.lower(), {})

        if sign_data and "interpretation" in sign_data:
            return sign_data["interpretation"]

        # Fallback to a generated interpretation
        house_meanings = {
            "1": "identity and self-expression",
            "2": "resources and values",
            "3": "communication and learning",
            "4": "home and family",
            "5": "creativity and pleasure",
            "6": "health and service",
            "7": "relationships and partnerships",
            "8": "transformation and shared resources",
            "9": "philosophy and higher learning",
            "10": "career and public image",
            "11": "community and aspirations",
            "12": "spirituality and subconscious",
        }

        sign_qualities = {
            "aries": "assertive and pioneering",
            "taurus": "stable and resourceful",
            "gemini": "curious and adaptable",
            "cancer": "nurturing and protective",
            "leo": "creative and expressive",
            "virgo": "analytical and practical",
            "libra": "harmonious and fair",
            "scorpio": "intense and transformative",
            "sagittarius": "adventurous and philosophical",
            "capricorn": "disciplined and ambitious",
            "aquarius": "innovative and humanitarian",
            "pisces": "intuitive and compassionate",
        }

        house_meaning = house_meanings.get(house, "unknown area")
        sign_quality = sign_qualities.get(sign.lower(), "unknown quality")

        return f"House {house} in {sign} - {house_meaning} - {sign_quality}"

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
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
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

        for i, p1 in enumerate(planet_list):
            for j in range(i + 1, len(planet_list)):
                p2 = planet_list[j]
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
                dignities[planet] = self._get_essential_dignity(planet, sign)
        return dignities

    def _get_all_planet_dignities(self, birth_chart: dict) -> dict:
        """Get dignities for all planets in the birth chart."""
        dignities = {}
        for planet, data in birth_chart.get("planets", {}).items():
            if planet in ("Ascendant", "Midheaven"):
                continue
            sign = data.get("sign", "")
            house = data.get("house")
            if sign and house is not None:
                dignities[planet] = self._get_essential_dignity(planet, sign)
        return dignities

    def _get_planet_interpretations(self) -> List[Dict[str, Any]]:
        """Generate interpretations for planets in the birth chart.

        Returns:
            List of dictionaries containing planet interpretations
        """
        planet_interpretations = []

        for planet in self.birth_chart.get("planets", []):
            name = planet.get("name")
            sign = planet.get("sign")
            house = planet.get("house")
            retrograde = planet.get("retrograde", False)

            if not name or not sign or house is None:
                continue

            # Get interpretation for this planet
            interpretation = f"{name} in {sign} (House {house})"
            if retrograde:
                interpretation += " Retrograde"

            # Get qualities for this planet
            planet_quality = ""
            sign_quality = ""
            house_meaning = ""

            # Try to get from structured data
            planet_data = self.structured_data.get("planets", {}).get(name.lower(), {})
            if planet_data:
                planet_quality = planet_data.get("qualities", "")

            sign_data = self.structured_data.get("signs", {}).get(sign.lower(), {})
            if sign_data:
                sign_quality = sign_data.get("qualities", "")

            house_data = self.structured_data.get("houses", {}).get(str(house), {})
            if house_data:
                house_meaning = house_data.get("meaning", "")

            # Add qualities to interpretation
            if planet_quality:
                interpretation += f" - {planet_quality}"
            if sign_quality:
                interpretation += f" - {sign_quality}"
            if house_meaning:
                interpretation += f" - {house_meaning}"

            # Create the planet interpretation object
            planet_interp = {
                "planet": name,
                "sign": sign,
                "house": house,
                "retrograde": retrograde,
                "interpretation": interpretation,
            }

            planet_interpretations.append(planet_interp)

        return planet_interpretations

    def _get_stellium_interpretation(self, sign: str, planets: List[str]) -> str:
        """Get interpretation for a stellium.

        Args:
            sign: Sign of the stellium
            planets: List of planets in the stellium

        Returns:
            String containing the interpretation
        """
        # Get element and modality of the sign
        element = self._get_sign_element(sign)
        modality = self._get_sign_modality(sign)

        # Get sign keywords
        sign_keywords = {
            "aries": "energetic, pioneering, assertive",
            "taurus": "steady, sensual, resourceful",
            "gemini": "communicative, versatile, curious",
            "cancer": "nurturing, protective, emotional",
            "leo": "creative, dramatic, proud",
            "virgo": "practical, analytical, service-oriented",
            "libra": "harmonious, fair, relationship-focused",
            "scorpio": "intense, transformative, powerful",
            "sagittarius": "philosophical, adventurous, truth-seeking",
            "capricorn": "ambitious, disciplined, systematic",
            "aquarius": "innovative, humanitarian, detached",
            "pisces": "compassionate, intuitive, spiritual",
        }

        # Get element qualities
        element_qualities = {
            "fire": "passionate, energetic, inspirational",
            "earth": "practical, stable, material",
            "air": "mental, communicative, objective",
            "water": "emotional, intuitive, sensitive",
        }

        # Get modality characteristics
        modality_chars = {
            "cardinal": "initiator, someone who starts projects and leads",
            "fixed": "stabilizer, someone who maintains and persists",
            "mutable": "adapter, someone who is flexible and can adjust to changing circumstances",
        }

        keywords = sign_keywords.get(sign.lower(), "")
        element_qual = element_qualities.get(element, "")
        modality_char = modality_chars.get(modality, "")

        return (
            f"Stellium in {sign} with {', '.join(planets)}. This concentration of energy in {sign} indicates "
            f"a strong focus on {keywords}. The {element} element gives strengths in {element_qual}. "
            f"A chart with dominant {modality.title()} energy indicates a {modality_char}."
        )

    def _get_element_emphasis_interpretation(self, element: str, planets: List[str]) -> str:
        """Get interpretation for an element emphasis.

        Args:
            element: Element with emphasis
            planets: List of planets in that element

        Returns:
            String containing the interpretation
        """
        element_descriptions = {
            "fire": "passion, energy, creativity, and inspiration. Fire dominant charts often indicate a person with enthusiasm, courage, and a need for action and self-expression. You approach life with vigor and spontaneity, though may need to be mindful of impulsiveness or burnout.",
            "earth": "practicality, stability, reliability, and material focus. Earth dominant charts often indicate a person with patience, realism, and a talent for manifesting tangible results. You approach life methodically and sensibly, though may need to be mindful of becoming too rigid or materialistic.",
            "air": "intellect, communication, social connection, and conceptual thinking. Air dominant charts often indicate a person with strong mental abilities, objectivity, and social intelligence. You approach life through analysis and exchange of ideas, though may need to be mindful of overthinking or detachment.",
            "water": "emotion, intuition, sensitivity, and connection. Water dominant charts often indicate a person with empathy, deep feeling, and psychological insight. You approach life through emotional attunement and intuitive understanding, though may need to be mindful of mood swings or becoming overwhelmed.",
        }

        return f"Emphasis on {element} element with planets: {', '.join(planets)}. This indicates a strong focus on {element_descriptions.get(element, 'qualities associated with this element')}."

    def _get_modality_emphasis_interpretation(self, modality: str, planets: List[str]) -> str:
        """Get interpretation for a modality emphasis.

        Args:
            modality: Modality with emphasis
            planets: List of planets in that modality

        Returns:
            String containing the interpretation
        """
        modality_descriptions = {
            "cardinal": "initiation, leadership, and pioneering action. Cardinal dominant charts often indicate someone who is proactive, ambitious, and oriented toward creating change. You excel at starting projects and taking the lead, though may need to work on follow-through and patience.",
            "fixed": "persistence, determination, and stability. Fixed dominant charts often indicate someone who is loyal, enduring, and resistant to change. You excel at maintaining momentum and seeing things through, though may need to work on flexibility and adapting to necessary changes.",
            "mutable": "adaptability, versatility, and responsiveness to change. Mutable dominant charts often indicate someone who is flexible, multifaceted, and able to thrive in changing circumstances. You excel at adjusting and serving varying needs, though may need to work on consistency and establishing clear boundaries.",
        }

        return f"Emphasis on {modality} modality with planets: {', '.join(planets)}. This indicates a strong focus on {modality_descriptions.get(modality, 'qualities associated with this modality')}."

    def _find_yod(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Yod (Finger of God) patterns in the aspects.

        Args:
            aspects: List of aspects in the birth chart

        Returns:
            List of dictionaries containing Yod pattern information
        """
        yods = []
        seen_combinations = set()

        # Group aspects by type
        sextiles = []
        quincunxes = []

        for aspect in aspects:
            aspect_type = aspect.get("type")
            # Handle numeric or string representation
            if aspect_type in [60, "60", "sextile"]:
                sextiles.append(aspect)
            elif aspect_type in [150, "150", "quincunx", "inconjunct"]:
                quincunxes.append(aspect)

        # Check each sextile for potential Yod
        for sextile in sextiles:
            planet1 = sextile["planet1"].lower()
            planet2 = sextile["planet2"].lower()

            # Look for quincunxes to a third planet
            for quincunx1 in quincunxes:
                if planet1 in [
                    quincunx1["planet1"].lower(),
                    quincunx1["planet2"].lower(),
                ]:
                    third_planet = (
                        quincunx1["planet2"]
                        if quincunx1["planet1"].lower() == planet1
                        else quincunx1["planet1"]
                    )

                    # Look for second quincunx
                    for quincunx2 in quincunxes:
                        if planet2 in [
                            quincunx2["planet1"].lower(),
                            quincunx2["planet2"].lower(),
                        ] and third_planet.lower() in [
                            quincunx2["planet1"].lower(),
                            quincunx2["planet2"].lower(),
                        ]:

                            # Found a Yod
                            planets = sorted([planet1, planet2, third_planet.lower()])
                            key = "-".join(planets)

                            if key not in seen_combinations:
                                seen_combinations.add(key)
                                yods.append({"planets": planets, "apex": third_planet.lower()})

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
            "neptune": "pisces",  # Modern rulership
            "pluto": "scorpio",  # Modern rulership
        }

        exaltation = {
            "sun": "aries",
            "moon": "taurus",
            "mercury": "virgo",
            "venus": "pisces",
            "mars": "capricorn",
            "jupiter": "cancer",
            "saturn": "libra",
            "uranus": "scorpio",  # Modern concept
            "neptune": "leo",  # Modern concept
            "pluto": "aquarius",  # Modern concept
        }

        detriment = {
            "sun": "aquarius",
            "moon": "capricorn",
            "mercury": ["sagittarius", "pisces"],
            "venus": ["aries", "scorpio"],
            "mars": ["libra", "taurus"],
            "jupiter": ["gemini", "virgo"],
            "saturn": ["cancer", "leo"],
            "uranus": "leo",  # Modern concept
            "neptune": "virgo",  # Modern concept
            "pluto": "taurus",  # Modern concept
        }

        fall = {
            "sun": "libra",
            "moon": "scorpio",
            "mercury": "pisces",
            "venus": "virgo",
            "mars": "cancer",
            "jupiter": "capricorn",
            "saturn": "aries",
            "uranus": "taurus",  # Modern concept
            "neptune": "aquarius",  # Modern concept
            "pluto": "leo",  # Modern concept
        }

        # Check rulership (strongest dignity)
        if (
            sign in rulership.get(planet, [])
            if isinstance(rulership.get(planet), list)
            else sign == rulership.get(planet)
        ):
            return "rulership"

        # Check exaltation
        if sign == exaltation.get(planet):
            return "exaltation"

        # Check detriment
        if (
            sign in detriment.get(planet, [])
            if isinstance(detriment.get(planet), list)
            else sign == detriment.get(planet)
        ):
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
        signs = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]

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
        signs = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]

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
            {
                "planets": ["mercury", "uranus"],
                "reason": "both intellectual and quick-thinking",
            },
            {"planets": ["venus", "neptune"], "reason": "both romantic and idealistic"},
            {
                "planets": ["mars", "pluto"],
                "reason": "both powerful and transformative",
            },
            {
                "planets": ["jupiter", "sun"],
                "reason": "both optimistic and growth-oriented",
            },
            {
                "planets": ["saturn", "mercury"],
                "reason": "both structured and detail-oriented",
            },
            {
                "planets": ["uranus", "mercury"],
                "reason": "both inventive and forward-thinking",
            },
            {"planets": ["neptune", "moon"], "reason": "both dreamy and empathic"},
            {"planets": ["pluto", "mars"], "reason": "both intense and focused"},
        ]

        # These pairs represent classic challenging relationships in astrology
        challenging_pairs = [
            {
                "planets": ["sun", "saturn"],
                "reason": "sun's expression can be limited by saturn's restrictions",
            },
            {
                "planets": ["moon", "mars"],
                "reason": "emotional sensitivity meets directness and aggression",
            },
            {
                "planets": ["mercury", "neptune"],
                "reason": "logical thinking clashes with dreaminess and confusion",
            },
            {
                "planets": ["venus", "pluto"],
                "reason": "harmony confronts intensity and control",
            },
            {
                "planets": ["mars", "saturn"],
                "reason": "action and drive meet limitation and delay",
            },
            {
                "planets": ["jupiter", "mercury"],
                "reason": "expansion conflicts with detailed analysis",
            },
            {
                "planets": ["saturn", "jupiter"],
                "reason": "restriction versus expansion creates tension",
            },
            {
                "planets": ["uranus", "venus"],
                "reason": "unpredictability challenges relationship harmony",
            },
            {
                "planets": ["neptune", "mercury"],
                "reason": "confusion disrupts clear communication",
            },
            {
                "planets": ["pluto", "sun"],
                "reason": "power struggles with self-expression",
            },
        ]

        # Check if our planets are in a harmonious pair
        for pair in harmonious_pairs:
            if planet1 in pair["planets"] and planet2 in pair["planets"]:
                return f"These planets work well together, being {pair['reason']}."

        # Check if our planets are in a challenging pair
        for pair in challenging_pairs:
            if planet1 in pair["planets"] and planet2 in pair["planets"]:
                return f"These planets can create tension, as {pair['reason']}."

        # For pairs not in our predefined lists, return a generic statement
        # based on traditional planetary qualities
        planetary_qualities = {
            "sun": {
                "element": "fire",
                "modality": "fixed",
                "nature": "warm, creative, expressive",
            },
            "moon": {
                "element": "water",
                "modality": "cardinal",
                "nature": "emotional, nurturing, responsive",
            },
            "mercury": {
                "element": "air",
                "modality": "mutable",
                "nature": "communicative, analytical, adaptable",
            },
            "venus": {
                "element": "earth/air",
                "modality": "fixed/cardinal",
                "nature": "harmonious, relational, artistic",
            },
            "mars": {
                "element": "fire",
                "modality": "cardinal",
                "nature": "active, assertive, energetic",
            },
            "jupiter": {
                "element": "fire",
                "modality": "mutable",
                "nature": "expansive, optimistic, growth-oriented",
            },
            "saturn": {
                "element": "earth",
                "modality": "cardinal",
                "nature": "structured, responsible, limiting",
            },
            "uranus": {
                "element": "air",
                "modality": "fixed",
                "nature": "innovative, unpredictable, freedom-seeking",
            },
            "neptune": {
                "element": "water",
                "modality": "mutable",
                "nature": "dreamy, spiritual, dissolving",
            },
            "pluto": {
                "element": "water",
                "modality": "fixed",
                "nature": "transformative, intense, powerful",
            },
        }

        # If both planets have defined qualities
        if planet1 in planetary_qualities and planet2 in planetary_qualities:
            p1_qualities = planetary_qualities[planet1]
            p2_qualities = planetary_qualities[planet2]

            # Determine compatibility based on elements
            element_compatibility = ""
            if p1_qualities["element"] == p2_qualities["element"]:
                element_compatibility = f"Both planets share the {p1_qualities['element']} element, creating natural harmony."
            elif (p1_qualities["element"] == "fire" and p2_qualities["element"] == "air") or (
                p1_qualities["element"] == "air" and p2_qualities["element"] == "fire"
            ):
                element_compatibility = "Fire and air elements complement each other, creating stimulation and inspiration."
            elif (p1_qualities["element"] == "earth" and p2_qualities["element"] == "water") or (
                p1_qualities["element"] == "water" and p2_qualities["element"] == "earth"
            ):
                element_compatibility = (
                    "Earth and water elements work well together, creating nurturing and stability."
                )
            else:
                # For other element combinations, we'll skip element compatibility
                pass

            # Create a general interpretation
            return f"{planet1.capitalize()} ({p1_qualities['nature']}) interacts with {planet2.capitalize()} ({p2_qualities['nature']}). {element_compatibility}"

        # Default return for unlisted planetary pairs
        return ""

    def interpret_birth_chart(self) -> Dict[str, Any]:
        """Generate a complete interpretation of the birth chart.

        Returns:
            Dictionary containing the complete birth chart interpretation
        """
        interpretation = {
            "planets": self._get_planet_interpretations(),
            "houses": self._get_house_interpretations(),
            "aspects": self._get_aspect_interpretations(),
            "patterns": self._get_pattern_interpretations(),
            "overall": self._get_overall_interpretation(),
        }

        return interpretation

    def _get_pattern_interpretations(self) -> Dict[str, Any]:
        """Find and interpret major aspect patterns in the birth chart.

        Returns:
            Dictionary containing interpretations of major aspect patterns
        """
        aspects = self.birth_chart.get("aspects", [])

        # Find major patterns
        grand_trines = self._find_grand_trine(aspects)
        t_squares = self._find_t_square(aspects)
        grand_crosses = self._find_grand_cross(aspects)
        yods = self._find_yod(aspects)

        # Find simple patterns like stelliums
        simple_patterns = self._analyze_simple_patterns(self.birth_chart)
        stelliums = [p for p in simple_patterns if p.get("type") == "stellium"]

        # Get interpretations for each pattern
        pattern_interpretations = {
            "grand_trines": [],
            "t_squares": [],
            "grand_crosses": [],
            "yods": [],
            "stelliums": [],
        }

        # Interpret Grand Trines
        for trine in grand_trines:
            planets = trine["planets"]
            element = trine["element"]

            interpretation = {
                "planets": planets,
                "element": element,
                "description": f"Grand Trine in {element} signs between {', '.join(planets)}. "
                f"This creates a harmonious flow of {element} energy, "
                f"indicating natural talents and easy expression in {element}-related areas. "
                f"While this brings ease, it can sometimes lead to complacency or taking the "
                f"path of least resistance. Your {element} element gifts come naturally.",
            }
            pattern_interpretations["grand_trines"].append(interpretation)

        # Interpret T-Squares
        for t_square in t_squares:
            planets = t_square["planets"]
            apex = t_square["apex"]

            # Find the other two planets
            other_planets = [p for p in planets if p != apex]

            interpretation = {
                "planets": planets,
                "apex": apex,
                "description": f"T-Square between {', '.join(planets)} with {apex} at the apex. "
                f"This creates dynamic tension that seeks resolution through {apex}. "
                f"The opposition between {other_planets[0]} and {other_planets[1]} "
                f"creates a polarity that is channeled through {apex}, requiring "
                f"active work to integrate these energies constructively.",
            }
            pattern_interpretations["t_squares"].append(interpretation)

        # Interpret Grand Crosses
        for cross in grand_crosses:
            planets = cross["planets"]
            modality = cross["modality"]

            interpretation = {
                "planets": planets,
                "modality": modality,
                "description": f"Grand Cross in {modality} signs between {', '.join(planets)}. "
                f"This creates a complex pattern of challenges and opportunities, "
                f"expressing through the {modality} mode of operation. "
                f"The four points of tension create a balanced but demanding energy "
                f"that pushes you toward achievement through overcoming obstacles.",
            }
            pattern_interpretations["grand_crosses"].append(interpretation)

        # Interpret Yods
        for yod_planets in yods:
            # The apex planet is at the quincunx point to the other two planets
            apex = yod_planets["apex"]
            base_planets = [p for p in yod_planets["planets"] if p != apex]

            interpretation = {
                "planets": yod_planets["planets"],
                "apex": apex,
                "description": f"Yod (Finger of God) with {apex} at the apex, connected by quincunxes to "
                f"{', '.join(base_planets)}, who share a sextile. "
                f"This pattern suggests a special destiny or mission involving {apex}, "
                f"requiring adjustments and integration of the seemingly unrelated energies "
                f"of {', '.join(base_planets)}.",
            }
            pattern_interpretations["yods"].append(interpretation)

        # Interpret Stelliums
        for stellium in stelliums:
            sign = stellium.get("sign")
            planets = stellium.get("planets", [])

            # Get element and modality of the sign
            sign_element = self._get_sign_element(sign)
            sign_modality = self._get_sign_modality(sign)

            interpretation = {
                "sign": sign,
                "planets": planets,
                "description": f"Stellium in {sign} with {', '.join(planets)}. "
                f"This concentration amplifies {sign} qualities in your chart. "
                f"The {sign_element} element and {sign_modality} modality are emphasized, "
                f"creating a focal point of energy that influences your entire chart. "
                f"With multiple planets in {sign}, there's a natural talent and focus "
                f"in areas related to this sign.",
            }
            pattern_interpretations["stelliums"].append(interpretation)

        return pattern_interpretations

    def _get_sign_element(self, sign: str) -> str:
        """Get the element of a sign.

        Args:
            sign: Sign name

        Returns:
            Element of the sign (fire, earth, air, water)
        """
        sign_elements = {
            "aries": "fire",
            "leo": "fire",
            "sagittarius": "fire",
            "taurus": "earth",
            "virgo": "earth",
            "capricorn": "earth",
            "gemini": "air",
            "libra": "air",
            "aquarius": "air",
            "cancer": "water",
            "scorpio": "water",
            "pisces": "water",
        }

        return sign_elements.get(sign.lower(), "unknown")

    def _get_sign_modality(self, sign: str) -> str:
        """Get the modality of a sign.

        Args:
            sign: Sign name

        Returns:
            Modality of the sign (cardinal, fixed, mutable)
        """
        sign_modalities = {
            "aries": "cardinal",
            "cancer": "cardinal",
            "libra": "cardinal",
            "capricorn": "cardinal",
            "taurus": "fixed",
            "leo": "fixed",
            "scorpio": "fixed",
            "aquarius": "fixed",
            "gemini": "mutable",
            "virgo": "mutable",
            "sagittarius": "mutable",
            "pisces": "mutable",
        }

        return sign_modalities.get(sign.lower(), "unknown")

    def _get_overall_interpretation(self) -> str:
        """Generate an overall interpretation of the birth chart.

        Returns:
            String containing the overall chart interpretation
        """
        # Get pattern counts
        patterns = self._get_pattern_interpretations()
        grand_trine_count = len(patterns["grand_trines"])
        t_square_count = len(patterns["t_squares"])
        grand_cross_count = len(patterns["grand_crosses"])

        # Get aspect counts by type
        aspects = self.birth_chart.get("aspects", [])
        aspect_counts = {}
        for aspect in aspects:
            aspect_type = aspect.get("type")
            # Normalize aspect type
            if aspect_type in [0, "0", "conjunction"]:
                key = "conjunctions"
            elif aspect_type in [60, "60", "sextile"]:
                key = "sextiles"
            elif aspect_type in [90, "90", "square"]:
                key = "squares"
            elif aspect_type in [120, "120", "trine"]:
                key = "trines"
            elif aspect_type in [180, "180", "opposition"]:
                key = "oppositions"
            else:
                continue
            aspect_counts[key] = aspect_counts.get(key, 0) + 1

        # Generate overall interpretation
        interpretation = []

        # Comment on major patterns
        if grand_trine_count > 0:
            interpretation.append(
                f"Your chart contains {grand_trine_count} Grand Trine{'s' if grand_trine_count > 1 else ''}, "
                "indicating areas of natural talent and harmonious energy flow."
            )

        if t_square_count > 0:
            interpretation.append(
                f"There {'are' if t_square_count > 1 else 'is'} {t_square_count} T-Square{'s' if t_square_count > 1 else ''} "
                "in your chart, suggesting areas of dynamic tension that can drive personal growth."
            )

        if grand_cross_count > 0:
            interpretation.append(
                f"Your chart features {grand_cross_count} Grand Cross{'es' if grand_cross_count > 1 else ''}, "
                "indicating complex challenges that can lead to significant achievements."
            )

        # Comment on aspect distribution
        harmonious = aspect_counts.get("trines", 0) + aspect_counts.get("sextiles", 0)
        challenging = aspect_counts.get("squares", 0) + aspect_counts.get("oppositions", 0)

        if harmonious > challenging:
            interpretation.append(
                "Your chart shows a predominance of harmonious aspects, suggesting natural flow and ease in many areas of life."
            )
        elif challenging > harmonious:
            interpretation.append(
                "Your chart features more challenging aspects, indicating opportunities for growth through overcoming obstacles."
            )
        else:
            interpretation.append(
                "Your chart shows a balanced mix of harmonious and challenging aspects, suggesting a well-rounded life experience."
            )

        return " ".join(interpretation)

    def _get_rising_sign_summary(self, rising_sign: str) -> str:
        """Generate a summary based on the rising sign.

        Args:
            rising_sign: Rising sign (Ascendant)

        Returns:
            Summary text
        """
        # Check if we have this in structured data
        rising_data = self.structured_data.get("rising", {}).get(rising_sign.lower(), {})

        if rising_data and "summary" in rising_data:
            return rising_data["summary"]

        # Fallback to a generated summary
        rising_descriptions = {
            "aries": "You project yourself as confident, direct, and pioneering. You approach life with enthusiasm and may come across as energetic and action-oriented.",
            "taurus": "You present yourself as reliable, steady, and practical. Others may perceive you as grounded, patient, and appreciative of beauty and comfort.",
            "gemini": "You come across as communicative, versatile, and curious. Your approach to life is adaptable and you may appear youthful and intellectually engaged.",
            "cancer": "You project sensitivity, nurturing, and emotional depth. You may appear protective of yourself and loved ones, with a strong connection to home and family.",
            "leo": "You present yourself with warmth, confidence, and creativity. Others may see you as charismatic, proud, and naturally drawing attention.",
            "virgo": "You come across as analytical, helpful, and detail-oriented. Your approach to life is practical and methodical, with a focus on improvement.",
            "libra": "You project harmony, fairness, and social grace. Others may see you as diplomatic, relationship-oriented, and appreciative of beauty.",
            "scorpio": "You present with intensity, depth, and a mysterious quality. Your approach to life may seem strategic and transformation-oriented.",
            "sagittarius": "You come across as optimistic, adventurous, and philosophical. Others may see you as straightforward, freedom-loving, and expansive in outlook.",
            "capricorn": "You project responsibility, ambition, and practicality. Your approach to life may seem disciplined, goal-oriented, and mindful of status.",
            "aquarius": "You present as original, independent, and humanitarian. Others may see you as forward-thinking, somewhat detached, and interested in community.",
            "pisces": "You come across as compassionate, intuitive, and adaptable. Your approach to life may seem dreamy, empathetic, and spiritually oriented.",
        }

        return rising_descriptions.get(
            rising_sign.lower(),
            f"With {rising_sign} rising, your personal approach and outward demeanor are colored by qualities associated with this sign.",
        )

    def _get_aspect_interpretations(self) -> List[Dict[str, Any]]:
        """Generate interpretations for aspects in the birth chart.

        Returns:
            List of dictionaries containing aspect interpretations
        """
        aspect_interpretations = []

        for aspect in self.birth_chart.get("aspects", []):
            planet1 = aspect.get("planet1")
            planet2 = aspect.get("planet2")
            aspect_type = aspect.get("type")
            orb = aspect.get("orb", 0)

            if not planet1 or not planet2 or not aspect_type:
                continue

            # Get basic aspect meaning
            aspect_meaning = ""
            if isinstance(aspect_type, (int, str)):
                aspect_type_str = str(aspect_type).lower()

                if aspect_type_str in ["0", "conjunction", "0"]:
                    aspect_meaning = "conjunction"
                elif aspect_type_str in ["60", "sextile"]:
                    aspect_meaning = "opportunity"
                elif aspect_type_str in ["90", "square"]:
                    aspect_meaning = "tension"
                elif aspect_type_str in ["120", "trine"]:
                    aspect_meaning = "harmony"
                elif aspect_type_str in ["180", "opposition"]:
                    aspect_meaning = "polarity"
                elif aspect_type_str in ["150", "quincunx", "inconjunct"]:
                    aspect_meaning = "adjustment"
                else:
                    aspect_meaning = "interacts with"

            # Get planet keywords
            planet1_keyword = self._get_planet_keyword(planet1)
            planet2_keyword = self._get_planet_keyword(planet2)

            # Generate basic interpretation
            interpretation = f"Your {planet1.lower()} ({planet1_keyword}) {aspect_meaning} your {planet2.lower()} ({planet2_keyword})."

            # Add orb significance
            if orb < 2:
                interpretation += " This aspect is very strong with a tight orb, making its influence particularly noticeable in your chart."
            elif orb < 4:
                interpretation += " This aspect is of moderate strength in your chart."
            else:
                interpretation += (
                    " With a wide orb, this aspect's influence is more subtle in your chart."
                )

            # Create the aspect interpretation object
            aspect_interp = {
                "planet1": planet1,
                "planet2": planet2,
                "type": aspect_type,
                "interpretation": interpretation,
            }

            aspect_interpretations.append(aspect_interp)

        return aspect_interpretations

    def _get_planet_keyword(self, planet_name: str) -> str:
        """Get a keyword for a planet.

        Args:
            planet_name: Name of the planet

        Returns:
            Keyword for the planet
        """
        keywords = {
            "sun": "essence",
            "moon": "emotions",
            "mercury": "communication",
            "venus": "love",
            "mars": "action",
            "jupiter": "expansion",
            "saturn": "structure",
            "uranus": "innovation",
            "neptune": "spirituality",
            "pluto": "transformation",
            "chiron": "healing",
            "north_node": "destiny",
            "south_node": "past",
            "ascendant": "identity",
            "midheaven": "purpose",
        }

        return keywords.get(planet_name.lower(), "energy")

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
        trines = []

        for aspect in aspects:
            aspect_type = aspect.get("type")
            # Handle numeric or string representation
            if aspect_type in [120, "120", "trine"]:
                trines.append(aspect)

        # Check each trine for potential Grand Trine
        for i, trine1 in enumerate(trines):
            planet1 = trine1["planet1"].lower()
            planet2 = trine1["planet2"].lower()

            for j, trine2 in enumerate(trines[i + 1 :], i + 1):
                if planet1 in [
                    trine2["planet1"].lower(),
                    trine2["planet2"].lower(),
                ] or planet2 in [trine2["planet1"].lower(), trine2["planet2"].lower()]:

                    # Get the third planet
                    third_planet = None
                    if planet1 == trine2["planet1"].lower():
                        third_planet = trine2["planet2"]
                    elif planet1 == trine2["planet2"].lower():
                        third_planet = trine2["planet1"]
                    elif planet2 == trine2["planet1"].lower():
                        third_planet = trine2["planet2"]
                    elif planet2 == trine2["planet2"].lower():
                        third_planet = trine2["planet1"]

                    if third_planet:
                        # Check for third trine
                        for trine3 in trines[j + 1 :]:
                            if third_planet.lower() in [
                                trine3["planet1"].lower(),
                                trine3["planet2"].lower(),
                            ] and (
                                planet1
                                in [
                                    trine3["planet1"].lower(),
                                    trine3["planet2"].lower(),
                                ]
                                or planet2
                                in [
                                    trine3["planet1"].lower(),
                                    trine3["planet2"].lower(),
                                ]
                            ):

                                # Found a Grand Trine
                                planets = sorted([planet1, planet2, third_planet.lower()])
                                key = "-".join(planets)

                                if key not in seen_combinations:
                                    seen_combinations.add(key)
                                    grand_trines.append(
                                        {
                                            "planets": planets,
                                            "element": self._get_trine_element(planets),
                                        }
                                    )

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
        for opposition in oppositions:
            planet1 = opposition["planet1"].lower()
            planet2 = opposition["planet2"].lower()

            # Look for squares to a third planet
            for square1 in squares:
                if planet1 in [square1["planet1"].lower(), square1["planet2"].lower()]:
                    third_planet = (
                        square1["planet2"]
                        if square1["planet1"].lower() == planet1
                        else square1["planet1"]
                    )

                    # Look for second square
                    for square2 in squares:
                        if planet2 in [
                            square2["planet1"].lower(),
                            square2["planet2"].lower(),
                        ] and third_planet.lower() in [
                            square2["planet1"].lower(),
                            square2["planet2"].lower(),
                        ]:

                            # Found a T-square
                            planets = sorted([planet1, planet2, third_planet.lower()])
                            key = "-".join(planets)

                            if key not in seen_combinations:
                                seen_combinations.add(key)
                                t_squares.append({"planets": planets, "apex": third_planet.lower()})

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
        squares = [a for a in aspects if a["type"] in [90, "90", "square"]]
        oppositions = [a for a in aspects if a["type"] in [180, "180", "opposition"]]

        # Check each pair of oppositions for potential Grand Cross
        for i, opp1 in enumerate(oppositions):
            planet1 = opp1["planet1"].lower()
            planet2 = opp1["planet2"].lower()

            for opp2 in oppositions[i + 1 :]:
                planet3 = opp2["planet1"].lower()
                planet4 = opp2["planet2"].lower()

                # Check if these planets are different
                if len({planet1, planet2, planet3, planet4}) == 4:
                    # Look for squares connecting these planets
                    square_count = 0
                    for square in squares:
                        sq_p1 = square["planet1"].lower()
                        sq_p2 = square["planet2"].lower()

                        if (sq_p1 in [planet1, planet2] and sq_p2 in [planet3, planet4]) or (
                            sq_p2 in [planet1, planet2] and sq_p1 in [planet3, planet4]
                        ):
                            square_count += 1

                    if square_count >= 4:  # Need at least 4 squares to form a Grand Cross
                        planets = sorted([planet1, planet2, planet3, planet4])
                        key = "-".join(planets)

                        if key not in seen_combinations:
                            seen_combinations.add(key)
                            grand_crosses.append(
                                {
                                    "planets": planets,
                                    "modality": self._get_cross_modality(planets),
                                }
                            )

        return grand_crosses

    def _get_trine_element(self, planets: List[str]) -> str:
        """Get the element of a Grand Trine based on the signs of the planets.

        Args:
            planets: List of planets in the Grand Trine

        Returns:
            Element of the Grand Trine (fire, earth, air, water) or None if not found
        """
        # Load planet positions from birth chart
        planet_signs = {}
        for planet in planets:
            planet_data = next(
                (p for p in self.birth_chart["planets"] if p["name"].lower() == planet.lower()),
                None,
            )
            if planet_data:
                planet_signs[planet] = planet_data["sign"].lower()

        # Check if we have all planet positions
        if len(planet_signs) != len(planets):
            return None

        # Get elements for each sign
        sign_elements = {
            "aries": "fire",
            "leo": "fire",
            "sagittarius": "fire",
            "taurus": "earth",
            "virgo": "earth",
            "capricorn": "earth",
            "gemini": "air",
            "libra": "air",
            "aquarius": "air",
            "cancer": "water",
            "scorpio": "water",
            "pisces": "water",
        }

        # Get elements for each planet's sign
        elements = {sign_elements.get(sign) for sign in planet_signs.values()}

        # If all planets are in signs of the same element, that's our Grand Trine element
        return elements.pop() if len(elements) == 1 else None

    def _get_cross_modality(self, planets: List[str]) -> str:
        """Get the modality of a Grand Cross based on the signs of the planets.

        Args:
            planets: List of planets in the Grand Cross

        Returns:
            Modality of the Grand Cross (cardinal, fixed, mutable) or None if not found
        """
        # Load planet positions from birth chart
        planet_signs = {}
        for planet in planets:
            planet_data = next(
                (p for p in self.birth_chart["planets"] if p["name"].lower() == planet.lower()),
                None,
            )
            if planet_data:
                planet_signs[planet] = planet_data["sign"].lower()

        # Check if we have all planet positions
        if len(planet_signs) != len(planets):
            return None

        # Get modalities for each sign
        sign_modalities = {
            "aries": "cardinal",
            "cancer": "cardinal",
            "libra": "cardinal",
            "capricorn": "cardinal",
            "taurus": "fixed",
            "leo": "fixed",
            "scorpio": "fixed",
            "aquarius": "fixed",
            "gemini": "mutable",
            "virgo": "mutable",
            "sagittarius": "mutable",
            "pisces": "mutable",
        }

        # Get modalities for each planet's sign
        modalities = {sign_modalities.get(sign) for sign in planet_signs.values()}

        # If all planets are in signs of the same modality, that's our Grand Cross modality
        return modalities.pop() if len(modalities) == 1 else None

    def _analyze_complex_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze birth chart for complex astrological patterns.

        Returns:
            Dictionary containing interpretations for various complex patterns
        """
        pattern_interpretations = {
            "grand_trines": [],
            "t_squares": [],
            "grand_crosses": [],
            "yods": [],
        }

        # Get aspects from birth chart
        aspects = self.birth_chart.get("aspects", [])

        # Find Grand Trines
        grand_trines = self._find_grand_trine(aspects)
        for trine in grand_trines:
            planets = trine["planets"]
            element = trine["element"]
            if element:
                element_meanings = {
                    "fire": "creative inspiration, intuition, and spiritual energy",
                    "earth": "practicality, stability, and material resources",
                    "air": "mental activity, communication, and social connection",
                    "water": "emotional depth, intuition, and compassion",
                }

                interpretation = {
                    "planets": planets,
                    "element": element,
                    "description": f"Grand Trine in {element} signs involving {', '.join(planets)}. "
                    f"This indicates an easy flow of {element_meanings.get(element, 'energy')} "
                    f"that may be taken for granted.",
                }
                pattern_interpretations["grand_trines"].append(interpretation)

        # Find T-Squares
        t_squares = self._find_t_square(aspects)
        for t_square in t_squares:
            planets = t_square["planets"]
            apex = t_square["apex"]

            interpretation = {
                "planets": planets,
                "apex": apex,
                "description": f"T-Square involving {', '.join(planets)} with {apex} at the apex. "
                f"This creates tension that drives action and achievement through {apex}.",
            }
            pattern_interpretations["t_squares"].append(interpretation)

        # Find Grand Crosses
        grand_crosses = self._find_grand_cross(aspects)
        for cross in grand_crosses:
            planets = cross["planets"]
            modality = cross["modality"]
            if modality:
                modality_meanings = {
                    "cardinal": "initiating action and leadership",
                    "fixed": "determination and resistance to change",
                    "mutable": "adaptability and communication",
                }

                interpretation = {
                    "planets": planets,
                    "modality": modality,
                    "description": f"Grand Cross in {modality} signs involving {', '.join(planets)}. "
                    f"This indicates intense tension and challenge related to {modality_meanings.get(modality, 'qualities')} "
                    f"that can lead to significant achievements.",
                }
                pattern_interpretations["grand_crosses"].append(interpretation)

        # Find Yods
        yods = self._find_yod(aspects)
        for yod_planets in yods:
            # The apex planet is at the quincunx point to the other two planets
            apex = yod_planets["apex"]
            base_planets = [p for p in yod_planets["planets"] if p != apex]

            interpretation = {
                "planets": yod_planets["planets"],
                "apex": apex,
                "description": f"Yod (Finger of God) with {apex} at the apex, connected by quincunxes to "
                f"{', '.join(base_planets)}, who share a sextile. "
                f"This pattern suggests a special destiny or mission involving {apex}, "
                f"requiring adjustments and integration of the seemingly unrelated energies "
                f"of {', '.join(base_planets)}.",
            }
            pattern_interpretations["yods"].append(interpretation)

        return pattern_interpretations

    def _analyze_simple_patterns(self, birth_chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze birth chart for simple astrological patterns like stelliums and element/modality emphasis.

        Args:
            birth_chart: Birth chart data to analyze

        Returns:
            List of dictionaries containing simple pattern information
        """
        patterns = []

        # Analyze stelliums (3 or more planets in the same sign)
        sign_counts = {}
        for planet in birth_chart.get("planets", []):
            # Skip points like Ascendant, MC, etc.
            if planet.get("name") in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                continue

            sign = planet.get("sign")
            if sign:
                sign_counts[sign] = sign_counts.get(sign, 0) + 1

        for sign, count in sign_counts.items():
            if count >= 3:  # Consider 3+ planets a stellium
                planets = [
                    p.get("name")
                    for p in birth_chart.get("planets", [])
                    if p.get("sign") == sign
                    and p.get("name") not in ["Ascendant", "Midheaven", "Descendant", "IC"]
                ]

                patterns.append(
                    {
                        "type": "stellium",
                        "sign": sign,
                        "planets": planets,
                        "count": count,
                    }
                )

        # Analyze element emphasis
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        element_planets = {"fire": [], "earth": [], "air": [], "water": []}

        for planet in birth_chart.get("planets", []):
            # Skip points like Ascendant, MC, etc.
            if planet.get("name") in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                continue

            sign = planet.get("sign", "").lower()
            element = self._get_sign_element(sign)

            if element in elements:
                elements[element] += 1
                element_planets[element].append(planet.get("name"))

        # Find emphasized elements (more than 1/4 of total planets)
        total_planets = sum(elements.values())
        threshold = total_planets / 4  # 25% is average

        for element, count in elements.items():
            if count > threshold + 1:  # At least 2 more than average
                patterns.append(
                    {
                        "type": "element_emphasis",
                        "element": element,
                        "planets": element_planets[element],
                        "count": count,
                    }
                )

            # Also note element lacking (1 or fewer planets)
            elif count <= threshold - 1:
                patterns.append({"type": "element_lack", "element": element, "count": count})

        # Analyze modality emphasis
        modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
        modality_planets = {"cardinal": [], "fixed": [], "mutable": []}

        for planet in birth_chart.get("planets", []):
            # Skip points like Ascendant, MC, etc.
            if planet.get("name") in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                continue

            sign = planet.get("sign", "").lower()
            modality = self._get_sign_modality(sign)

            if modality in modalities:
                modalities[modality] += 1
                modality_planets[modality].append(planet.get("name"))

        # Find emphasized modalities (more than 1/3 of total planets)
        threshold = total_planets / 3  # 33% is average

        for modality, count in modalities.items():
            if count > threshold + 1:  # At least 2 more than average
                patterns.append(
                    {
                        "type": "modality_emphasis",
                        "modality": modality,
                        "planets": modality_planets[modality],
                        "count": count,
                    }
                )

            # Also note modality lacking (1 or fewer planets)
            elif count <= threshold - 1:
                patterns.append({"type": "modality_lack", "modality": modality, "count": count})

        return patterns

    def _analyze_simple_element_balance(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze birth chart for element balance.

        Args:
            birth_chart: Birth chart data to analyze

        Returns:
            Dictionary containing element balance information
        """
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        element_planets = {"fire": [], "earth": [], "air": [], "water": []}

        for planet in birth_chart.get("planets", []):
            # Skip points like Ascendant, MC, etc.
            if planet.get("name") in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                continue

            sign = planet.get("sign", "").lower()
            element = self._get_sign_element(sign)

            if element in elements:
                elements[element] += 1
                element_planets[element].append(planet.get("name"))

        # Calculate percentages
        total_planets = sum(elements.values())
        percentages = {
            element: (count / total_planets) * 100 if total_planets > 0 else 0
            for element, count in elements.items()
        }

        # Determine dominant and lacking elements
        sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_elements[0][0] if sorted_elements[0][1] > 0 else None
        lacking = [elem for elem, count in elements.items() if count <= 1]

        # Generate interpretation text
        interpretation = self._generate_element_balance_interpretation(
            dominant, lacking, percentages
        )

        return {
            "counts": elements,
            "percentages": percentages,
            "dominant": dominant,
            "lacking": lacking,
            "planets": element_planets,
            "interpretation": interpretation,
        }

    def _generate_element_balance_interpretation(
        self, dominant: str, lacking: List[str], percentages: Dict[str, float]
    ) -> str:
        """Generate interpretation text for element balance.

        Args:
            dominant: Dominant element (if any)
            lacking: List of lacking elements
            percentages: Percentages of each element

        Returns:
            Interpretation text
        """
        element_descriptions = {
            "fire": "passion, creativity, and assertiveness",
            "earth": "practicality, stability, and material focus",
            "air": "mental activity, communication, and social connection",
            "water": "emotional depth, intuition, and sensitivity",
        }

        interpretation_parts = []

        # Describe dominant element
        if dominant:
            percentage = round(percentages[dominant])
            interpretation_parts.append(
                f"Your chart emphasizes the {dominant} element ({percentage}% of planets), "
                f"suggesting a strong focus on {element_descriptions.get(dominant)}."
            )

        # Describe lacking elements
        if lacking:
            if len(lacking) == 1:
                lacking_element = lacking[0]
                interpretation_parts.append(
                    f"Your chart shows limited {lacking_element} element energy, which may mean "
                    f"{element_descriptions.get(lacking_element)} could be areas for conscious development."
                )
            else:
                lacking_elements = ", ".join(lacking)
                interpretation_parts.append(
                    f"Your chart shows limited {lacking_elements} elements, suggesting areas "
                    f"for conscious development in qualities associated with these elements."
                )

        # Note balance if neither dominant nor lacking elements
        if not dominant and not lacking:
            interpretation_parts.append(
                "Your chart shows a relatively balanced distribution of elements, "
                "suggesting versatility in approaching life through different modes of expression."
            )

        return " ".join(interpretation_parts)

    def _analyze_simple_modality_balance(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze birth chart for modality balance.

        Args:
            birth_chart: Birth chart data to analyze

        Returns:
            Dictionary containing modality balance information
        """
        modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
        modality_planets = {"cardinal": [], "fixed": [], "mutable": []}

        for planet in birth_chart.get("planets", []):
            # Skip points like Ascendant, MC, etc.
            if planet.get("name") in ["Ascendant", "Midheaven", "Descendant", "IC"]:
                continue

            sign = planet.get("sign", "").lower()
            modality = self._get_sign_modality(sign)

            if modality in modalities:
                modalities[modality] += 1
                modality_planets[modality].append(planet.get("name"))

            # Calculate percentages
            total_planets = sum(modalities.values())
            percentages = {
                modality: (count / total_planets) * 100 if total_planets > 0 else 0
                for modality, count in modalities.items()
            }

            # Determine dominant and lacking modalities
            sorted_modalities = sorted(modalities.items(), key=lambda x: x[1], reverse=True)
            dominant = sorted_modalities[0][0] if sorted_modalities[0][1] > 0 else None
            lacking = [mod for mod, count in modalities.items() if count <= 1]

            # Generate interpretation text
            interpretation = self._generate_modality_balance_interpretation(
                dominant, lacking, percentages
            )

            return {
                "counts": modalities,
                "percentages": percentages,
                "dominant": dominant,
                "lacking": lacking,
                "planets": modality_planets,
                "interpretation": interpretation,
            }

    def _generate_modality_balance_interpretation(
        self, dominant: str, lacking: List[str], percentages: Dict[str, float]
    ) -> str:
        """Generate interpretation text for modality balance.

        Args:
            dominant: Dominant modality (if any)
            lacking: List of lacking modalities
            percentages: Percentages of each modality

        Returns:
            Interpretation text
        """
        modality_descriptions = {
            "cardinal": "initiating action, leadership, and pioneering",
            "fixed": "persistence, stability, and determination",
            "mutable": "adaptability, flexibility, and versatility",
        }

        interpretation_parts = []

        # Describe dominant modality
        if dominant:
            percentage = round(percentages[dominant])
            interpretation_parts.append(
                f"Your chart emphasizes the {dominant} modality ({percentage}% of planets), "
                f"suggesting a strong focus on {modality_descriptions.get(dominant)}."
            )

        # Describe lacking modalities
        if lacking:
            if len(lacking) == 1:
                lacking_modality = lacking[0]
                interpretation_parts.append(
                    f"Your chart shows limited {lacking_modality} modality energy, which may mean "
                    f"{modality_descriptions.get(lacking_modality)} could be areas for conscious development."
                )
            else:
                lacking_modalities = ", ".join(lacking)
                interpretation_parts.append(
                    f"Your chart shows limited {lacking_modalities} modalities, suggesting areas "
                    f"for conscious development in qualities associated with these modalities."
                )

        # Note balance if neither dominant nor lacking modalities
        if not dominant and not lacking:
            interpretation_parts.append(
                "Your chart shows a relatively balanced distribution of modalities, "
                "suggesting versatility in how you approach initiation, stabilization, and adaptation."
            )

        return " ".join(interpretation_parts)

    def _analyze_combinations(self, birth_chart: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze birth chart for significant planetary combinations.

        Args:
            birth_chart: Birth chart data to analyze

        Returns:
            List of dictionaries containing combination interpretations
        """
        combinations = []

        # Get all planet positions
        planet_positions = {}
        for planet in birth_chart.get("planets", []):
            name = planet.get("name", "").lower()
            sign = planet.get("sign", "").lower()
            if name and sign:
                planet_positions[name] = sign

        # Analyze Sun-Moon combination
        if "sun" in planet_positions and "moon" in planet_positions:
            sun_sign = planet_positions["sun"]
            moon_sign = planet_positions["moon"]

            # Check if we have this combination in the structured data
            sun_moon_data = self.structured_data.get("combinations", {}).get("sun_moon", {})
            combo_key = f"{sun_sign}_{moon_sign}"

            if combo_key in sun_moon_data:
                combinations.append(
                    {
                        "type": "sun_moon",
                        "sun_sign": sun_sign,
                        "moon_sign": moon_sign,
                        "interpretation": sun_moon_data[combo_key],
                    }
                )
            else:
                # Generate a simple interpretation
                interpretation = self._generate_sun_moon_interpretation(sun_sign, moon_sign)
                combinations.append(
                    {
                        "type": "sun_moon",
                        "sun_sign": sun_sign,
                        "moon_sign": moon_sign,
                        "interpretation": interpretation,
                    }
                )

        # Analyze Mercury-Venus combination (communication and values)
        if "mercury" in planet_positions and "venus" in planet_positions:
            mercury_sign = planet_positions["mercury"]
            venus_sign = planet_positions["venus"]
            interpretation = self._generate_mercury_venus_interpretation(mercury_sign, venus_sign)
            combinations.append(
                {
                    "type": "mercury_venus",
                    "mercury_sign": mercury_sign,
                    "venus_sign": venus_sign,
                    "interpretation": interpretation,
                }
            )

        # Analyze Mars-Venus combination (action and attraction)
        if "mars" in planet_positions and "venus" in planet_positions:
            mars_sign = planet_positions["mars"]
            venus_sign = planet_positions["venus"]
            interpretation = self._generate_mars_venus_interpretation(mars_sign, venus_sign)
            combinations.append(
                {
                    "type": "mars_venus",
                    "mars_sign": mars_sign,
                    "venus_sign": venus_sign,
                    "interpretation": interpretation,
                }
            )

        # Analyze Jupiter-Saturn combination (expansion and limitation)
        if "jupiter" in planet_positions and "saturn" in planet_positions:
            jupiter_sign = planet_positions["jupiter"]
            saturn_sign = planet_positions["saturn"]
            interpretation = self._generate_jupiter_saturn_interpretation(jupiter_sign, saturn_sign)
            combinations.append(
                {
                    "type": "jupiter_saturn",
                    "jupiter_sign": jupiter_sign,
                    "saturn_sign": saturn_sign,
                    "interpretation": interpretation,
                }
            )

        return combinations

    def _generate_mercury_venus_interpretation(self, mercury_sign: str, venus_sign: str) -> str:
        """Generate interpretation for Mercury-Venus combination."""
        mercury_element = self._get_sign_element(mercury_sign)
        venus_element = self._get_sign_element(venus_sign)

        base_text = (
            f"Your Mercury in {mercury_sign.capitalize()} and Venus in "
            f"{venus_sign.capitalize()} shows how you combine communication "
            f"with values and relationships. "
        )

        if mercury_element == venus_element:
            base_text += (
                f"With both planets in {mercury_element} signs, your thoughts "
                f"and values flow naturally together, "
            )
            if mercury_element == "fire":
                base_text += "expressing yourself with enthusiasm and creativity."
            elif mercury_element == "earth":
                base_text += "giving you practical and grounded communication in relationships."
            elif mercury_element == "air":
                base_text += "enhancing your intellectual approach to relationships and values."
            else:  # water
                base_text += "deepening your emotional understanding and expression."
        else:
            base_text += (
                f"Mercury in a {mercury_element} sign and Venus in a "
                f"{venus_element} sign suggests you bridge different modes "
                f"of expression in relationships."
            )

        return base_text

    def _generate_mars_venus_interpretation(self, mars_sign: str, venus_sign: str) -> str:
        """Generate interpretation for Mars-Venus combination."""
        mars_element = self._get_sign_element(mars_sign)
        venus_element = self._get_sign_element(venus_sign)

        base_text = (
            f"Your Mars in {mars_sign.capitalize()} and Venus in "
            f"{venus_sign.capitalize()} describes your approach to "
            f"attraction and action. "
        )

        if mars_element == venus_element:
            base_text += (
                f"Both planets in {mars_element} signs suggest harmony "
                f"between your desires and actions. "
            )
            if mars_element == "fire":
                base_text += "You pursue relationships with passion and directness."
            elif mars_element == "earth":
                base_text += "You take a practical and steady approach to relationships."
            elif mars_element == "air":
                base_text += (
                    "You approach relationships with intellectual curiosity and social grace."
                )
            else:  # water
                base_text += "You navigate relationships with emotional intelligence and intuition."
        else:
            base_text += (
                f"Mars in a {mars_element} sign and Venus in a {venus_element} "
                f"sign indicates you balance different energies in relationships "
                f"and pursuit of desires."
            )

        return base_text

    def _generate_jupiter_saturn_interpretation(self, jupiter_sign: str, saturn_sign: str) -> str:
        """Generate interpretation for Jupiter-Saturn combination."""
        jupiter_element = self._get_sign_element(jupiter_sign)
        saturn_element = self._get_sign_element(saturn_sign)

        base_text = (
            f"Your Jupiter in {jupiter_sign.capitalize()} and Saturn in "
            f"{saturn_sign.capitalize()} reflects the balance between "
            f"expansion and limitation in your life. "
        )

        if jupiter_element == saturn_element:
            base_text += (
                f"Both planets in {jupiter_element} signs suggest natural "
                f"integration of growth and structure. "
            )
            if jupiter_element == "fire":
                base_text += "You combine enthusiasm with disciplined action."
            elif jupiter_element == "earth":
                base_text += "You expand through practical and methodical approaches."
            elif jupiter_element == "air":
                base_text += "You grow through intellectual understanding and structured learning."
            else:  # water
                base_text += "You develop through emotional wisdom and spiritual discipline."
        else:
            base_text += (
                f"Jupiter in a {jupiter_element} sign and Saturn in a "
                f"{saturn_element} sign indicates you navigate between "
                f"different approaches to growth and responsibility."
            )

        return base_text

    def _generate_sun_moon_interpretation(self, sun_sign: str, moon_sign: str) -> str:
        """Generate an interpretation for a Sun-Moon combination.

        Args:
            sun_sign: Sun sign
            moon_sign: Moon sign

        Returns:
            Interpretation text
        """
        # Get qualities of each sign
        sun_element = self._get_sign_element(sun_sign)
        sun_modality = self._get_sign_modality(sun_sign)
        moon_element = self._get_sign_element(moon_sign)
        moon_modality = self._get_sign_modality(moon_sign)

        # Element combinations with descriptions split across lines
        element_combos = {
            ("fire", "fire"): ("double fire intensity that fuels your passion and creativity"),
            ("fire", "earth"): "a balance between inspiration and practicality",
            ("fire", "air"): "creative thinking and passionate communication",
            ("fire", "water"): "passionate emotions and creative intuition",
            ("earth", "fire"): "practical action and grounded creativity",
            ("earth", "earth"): (
                "double earth influence that emphasizes stability and practicality"
            ),
            ("earth", "air"): "practical thinking and structured communication",
            ("earth", "water"): "emotional security and practical intuition",
            ("air", "fire"): "intellectual passion and communicative creativity",
            ("air", "earth"): "ideas that can be practically implemented",
            ("air", "air"): ("double air emphasis that enhances intellectual and social abilities"),
            ("air", "water"): "intuitive thinking and emotional communication",
            ("water", "fire"): "emotional passion and intuitive creativity",
            ("water", "earth"): "emotional grounding and intuitive practicality",
            ("water", "air"): "emotional understanding and intuitive communication",
            ("water", "water"): (
                "double water emphasis that deepens emotional and intuitive abilities"
            ),
        }

        # Generate interpretation
        element_combo = element_combos.get(
            (sun_element, moon_element), "a complex blend of energies"
        )

        # Build interpretation text in parts
        sun_moon_text = (
            f"Your Sun in {sun_sign.capitalize()} and Moon in "
            f"{moon_sign.capitalize()} creates {element_combo}. "
        )

        identity_text = (
            f"Your {sun_modality} {sun_element} Sun represents your conscious "
            f"identity, while your {moon_modality} {moon_element} Moon shapes "
            f"your emotional nature. "
        )

        integration_text = (
            "This combination suggests that your core self and emotional needs "
            f"{'complement each other well' if sun_element == moon_element else 'require some integration'}."
        )

        return sun_moon_text + identity_text + integration_text
