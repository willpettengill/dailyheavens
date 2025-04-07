"""Astrological interpretation service module."""

# Standard library imports
from datetime import datetime
import json
import logging
import math
import os
import random
import re
import warnings
from typing import Dict, Any, List, Tuple, Union, Optional

# Third-party imports
from jinja2 import Environment, FileSystemLoader
from flatlib.datetime import Datetime
import markdown2

# Local application imports
from app.services.birth_chart import BirthChartService
from app.services.chart_statistics import ChartStatisticsService

# Configure module logger
logger = logging.getLogger(__name__)
# Set a higher logging level for this module to see the detailed logs
logger.setLevel(logging.DEBUG)


class InterpretationService:
    """Astrological interpretation service that generates detailed birth chart analyses.

    This service provides methods for analyzing birth charts, detecting astrological patterns,
    and generating interpretations based on planetary positions, house placements,
    aspects, and other astrological factors.
    """

    def __init__(self, logger=None):
        """Initialize the interpretation service.

        Args:
            logger: Optional logger instance
        """
        # Configure logging
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            # Set to DEBUG for detailed logs
            self.logger.setLevel(logging.DEBUG)

        self.logger.info("Initializing InterpretationService")

        # Set project root for file paths
        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))
        self.logger.debug(f"Project root: {self.project_root}")

        # Initialize data structures
        self.structured_data = {}
        self.birth_chart = None

        # Initialize caches
        self._aspect_cache = {}
        self._planet_cache = {}
        self._house_cache = {}
        self._sign_cache = {}

        # Set up Jinja2 for template rendering
        templates_dir = os.path.join(self.project_root, "app", "templates")
        self.logger.debug(f"Templates directory: {templates_dir}")
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load structured data
        self._load_all_structured_data()

        # Initialize caches after loading data
        self._initialize_caches()

        self.logger.info("InterpretationService initialized successfully")

    def _load_all_structured_data(self):
        """Load all structured data from JSON files."""
        self.logger.info("Loading all structured data files")
        structured_data_dir = os.path.join(
            self.project_root, "data", "structured")

        try:
            # Get all JSON files in the structured data directory
            if not os.path.exists(structured_data_dir):
                self.logger.error(
                    f"Structured data directory not found: {structured_data_dir}")
                return

            json_files = [f.replace('.json', '') for f in os.listdir(
                structured_data_dir) if f.endswith('.json')]
            self.logger.debug(
                f"Found {len(json_files)} JSON files: {json_files}")

            # Load each file
            for file_name in json_files:
                self.structured_data[file_name] = self._load_structured_data(
                    file_name)

            # Log loaded data sources
            self.logger.info(
                f"Loaded structured data sources: {list(self.structured_data.keys())}")

            # Convert numeric aspect types to strings for consistency
            if "aspects" in self.structured_data:
                aspect_data = self.structured_data["aspects"]
                aspect_types_to_add = {}

                for key, data in list(aspect_data.items()):
                    if "angle" in data:
                        angle_str = str(data["angle"])
                        self.logger.debug(
                            f"Converting aspect type {key} to numeric key {angle_str}")
                        aspect_types_to_add[angle_str] = data

            # Add the new aspect types separately
            # Ensure this block is correctly indented if it belongs to the 'if "aspects" in ...' block
            # Assuming it belongs, based on context:
            if "aspects" in self.structured_data:  # Re-check needed if logic differs
                for angle, data in aspect_types_to_add.items():
                    if angle not in aspect_data:
                        aspect_data[angle] = data

            # Check if descriptions is loaded
            if "descriptions" in self.structured_data:
                self.logger.info("Descriptions data loaded successfully")
                if isinstance(self.structured_data["descriptions"], dict):
                    self.logger.debug(
                        f"Available keys in descriptions: {list(self.structured_data['descriptions'].keys())}"
                    )
            else:
                self.logger.warning("Descriptions data not loaded!")

        except Exception as e:
            self.logger.error(
                f"Error loading all structured data: {str(e)}",
                exc_info=True)

    def _load_structured_data(self, file_name: str) -> Dict:
        """Load structured data from JSON files.

        Args:
            file_name: Name of the JSON file to load

        Returns:
            Dictionary containing the structured data
        """
        self.logger.debug(f"Loading structured data file: {file_name}")
        structured_data_dir = os.path.join(
            self.project_root, "data", "structured")
        file_path = os.path.join(structured_data_dir, f"{file_name}.json")

        try:
            if not os.path.exists(file_path):
                self.logger.warning(
                    f"Structured data file not found: {file_path}")
                return {}

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.debug(
                    f"Successfully loaded {file_name}.json with {len(data)} top-level keys")

                # Log the top-level keys to understand structure
                if isinstance(data, dict):
                    self.logger.debug(
                        f"Top-level keys in {file_name}.json: {list(data.keys())}")
                elif isinstance(data, list):
                    self.logger.debug(
                        f"Loaded list data from {file_name}.json with {len(data)} items")

                return data
        except json.JSONDecodeError:
            self.logger.error(f"Error parsing JSON from {file_path}")
            return {}
        except Exception as e:
            self.logger.error(
                f"Error loading structured data from {file_path}: {str(e)}")
            return {}

    def _initialize_caches(self):
        """Initialize caches with data from structured_data."""
        try:
            # Initialize planet cache
            planets_data = self.structured_data.get("planets", {})
            if planets_data:
                self._planet_cache = dict((k.lower(), v)
                                          for k, v in planets_data.items())

            # Initialize sign cache
            signs_data = self.structured_data.get("signs", {})
            if signs_data:
                self._sign_cache = dict((k.lower(), v)
                                        for k, v in signs_data.items())

            # Initialize house cache
            houses_data = self.structured_data.get("houses", {})
            if houses_data:
                self._house_cache = {k: v for k, v in houses_data.items()}

            # Initialize aspect cache
            aspects_data = self.structured_data.get("aspects", {})
            if aspects_data:
                self._aspect_cache = {
                    k.lower(): v for k, v in aspects_data.items()}

            # Add numeric keys to aspect cache - using a copy to avoid mutation
            # during iteration
            aspect_types_to_add = {}

            for key, data in list(self._aspect_cache.items()):
                if "angle" in data:
                    angle_str = str(data["angle"])
                    # Use the key in logging to avoid the unused variable
                    # warning
                    self.logger.debug(
                        f"Converting aspect type {key} to numeric key {angle_str}")
                    aspect_types_to_add[angle_str] = data

            # Add the new aspect types separately
            for angle_str, data in aspect_types_to_add.items():
                if angle_str not in self._aspect_cache:
                    self._aspect_cache[angle_str] = data

            self.logger.debug("Successfully initialized caches")
        except Exception as e:
            self.logger.error(
                f"Error initializing caches: {str(e)}",
                exc_info=True)

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

    def _get_element_modality_qualities_simple(
            self, element: str, modality: str) -> List[str]:
        """Get qualities for element-modality combination without using enums."""
        qualities = []
        if element == "fire":
            if modality == "cardinal":
                qualities.extend(["dynamic", "initiative", "leadership"])
            elif modality == "fixed":
                qualities.extend(["stability", "determination", "persistence"])
            else:  # mutable
                qualities.extend(
                    ["adaptability", "versatility", "flexibility"])
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

    def _get_element_modality_keywords_simple(
            self, element: str, modality: str) -> List[str]:
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

    def _get_element_keywords_simple(self, element: str, modality: str = None) -> List[str]:
        """Get general keywords for an element, optionally filtered by modality.
        
        Args:
            element: The astrological element (fire, earth, air, water)
            modality: Optional modality to filter keywords (cardinal, fixed, mutable)
            
        Returns:
            List of keywords associated with the element
        """
        keywords = []
        if element == "fire":
            keywords.extend(["energy", "passion", "action", "inspiration", "creativity"])
            if modality:
                return self._get_element_modality_keywords_simple(element, modality)
        elif element == "earth":
            keywords.extend(["stability", "practicality", "reliability", "structure", "material"])
            if modality:
                return self._get_element_modality_keywords_simple(element, modality)
        elif element == "air":
            keywords.extend(["intellect", "communication", "social", "ideas", "perspective"])
            if modality:
                return self._get_element_modality_keywords_simple(element, modality)
        elif element == "water":
            keywords.extend(["emotion", "intuition", "sensitivity", "flow", "connection"])
            if modality:
                return self._get_element_modality_keywords_simple(element, modality)
        return keywords

    def _validate_birth_chart(self, birth_chart: Dict[str, Any]) -> bool:
        """Validate birth chart data structure.

        Args:
            birth_chart: Birth chart data

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

        # Check planets are a dictionary or list
        planets = birth_chart.get("planets", {})

        # Handle dictionary format (new format)
        if isinstance(planets, dict):
            self.logger.debug("Processing dictionary format for planets")

            # Check each planet has the required fields
            for planet_name, planet_data in planets.items():
                if not isinstance(planet_data, dict):
                    self.logger.error(
                        f"Planet {planet_name} data must be a dictionary")
                    return False

                if "sign" not in planet_data:
                    self.logger.error(f"Planet {planet_name} must have a sign")
                    return False

        # Handle list format (old format)
        elif isinstance(planets, list):
            self.logger.debug("Processing list format for planets")

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
        else:
            self.logger.error("Planets must be either a dictionary or a list")
            return False

        # Check for houses (optional but recommended)
        houses = birth_chart.get("houses", {})

        # Handle dictionary format for houses
        if isinstance(houses, dict):
            self.logger.debug("Processing dictionary format for houses")
            # Dictionary format is fine as is
            pass
        # Handle list format for houses
        elif isinstance(houses, list) and houses:
            self.logger.debug("Processing list format for houses")
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
        elif houses and not isinstance(houses, (dict, list)):
            self.logger.error("Houses must be either a dictionary or a list")
            return False

        # Check for aspects (optional but recommended)
        aspects = birth_chart.get("aspects", [])
        if aspects and not isinstance(aspects, list):
            self.logger.error("Aspects must be a list")
            return False

        # All checks passed
        self.logger.debug("Birth chart validation passed")
        return True

    def _validate_interpretation_request(
            self, request: Dict) -> Tuple[bool, str]:
        """Validate the interpretation request.

        Args:
            request: The interpretation request to validate

        Returns:
            A tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            if not request.get("birth_chart") and not all(
                request.get(field) for field in [
                    "date_of_birth", "latitude", "longitude"]):
                return (
                    False,
                    "Either birth_chart or date_of_birth, latitude, and longitude must be provided",
                )

            # Validate date_of_birth if provided
            if request.get("date_of_birth"):
                try:
                    datetime.fromisoformat(
                        request["date_of_birth"].replace(
                            "Z", "+00:00"))
                except ValueError:
                    return (
                        False, "Invalid date_of_birth format. Use ISO format (YYYY-MM-DDTHH:MM:SS)", )

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
            logger.error(
                f"Error validating interpretation request: {str(e)}",
                exc_info=True)
            return False, str(e)

    def generate_interpretation(
            self,
            birth_chart: Dict,
            level: str = "basic") -> Dict:
        """Generate an interpretation based on the birth chart.

        Args:
            birth_chart: Birth chart data with planets, houses, aspects
            level: Interpretation detail level ('basic', 'intermediate', 'detailed')

        Returns:
            Dictionary containing interpretation data
        """
        self.logger.info(f"Generating {level} interpretation for birth chart")

        try:
            # Validate birth chart data
            if not self._validate_birth_chart(birth_chart):
                self.logger.error("Invalid birth chart data")
                return {
                    "error": "Invalid birth chart data",
                    "success": False
                }

            # Check if birth chart has planets
            if not birth_chart.get("planets"):
                self.logger.error("Birth chart has no planets")
                return {
                    "error": "Birth chart has no planets",
                    "success": False
                }

            # Create interpretation object
            interpretation = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "description": f"{level.capitalize()} interpretation of the birth chart",
            }

            # Add planet interpretations
            self.logger.debug("Generating planet interpretations")
            planet_interpretations = self._generate_planet_interpretations(
                birth_chart, level)
            interpretation["planets"] = planet_interpretations
            self.logger.debug(
                f"Generated interpretations for {len(planet_interpretations)} planets")

            # Add house interpretations
            self.logger.debug("Generating house interpretations")
            house_interpretations = self._generate_house_interpretations(
                birth_chart, level)
            interpretation["houses"] = house_interpretations
            self.logger.debug(
                f"Generated interpretations for {len(house_interpretations)} houses")

            # Add aspect interpretations
            self.logger.debug("Generating aspect interpretations")
            aspect_interpretations = self._generate_aspect_interpretations(
                birth_chart, level)
            interpretation["aspects"] = aspect_interpretations
            self.logger.debug(
                f"Generated interpretations for {len(aspect_interpretations)} aspects")

            # Get element balance
            element_balance = self._analyze_simple_element_balance(birth_chart)
            interpretation["element_balance"] = element_balance

            # Get modality balance
            modality_balance = self._analyze_simple_modality_balance(birth_chart)
            interpretation["modality_balance"] = modality_balance

            # Get simple patterns (stelliums, house emphasis)
            simple_patterns = self._analyze_simple_patterns(birth_chart)
            interpretation["simple_patterns"] = simple_patterns

            # Get pattern interpretations (complex)
            self.logger.debug("Analyzing complex patterns")
            pattern_interpretations = self._analyze_complex_patterns(
                birth_chart, level)
            interpretation["patterns"] = pattern_interpretations
            self.logger.debug(
                f"Analyzed {len(pattern_interpretations)} complex patterns")

            # Get planet combinations
            combinations = self._analyze_combinations(birth_chart)
            interpretation["combinations"] = combinations

            # Generate overall interpretation
            self.logger.debug("Generating overall interpretation")
            overall = self._generate_overall_interpretation(birth_chart, level)
            interpretation["overall"] = overall
            self.logger.debug("Overall interpretation generated")

            # Get rising sign interpretation
            asc_sign = birth_chart.get("angles", {}).get("ascendant", {}).get("sign")
            if asc_sign:
                rising_summary = self._get_rising_sign_summary(asc_sign)
                interpretation["rising_summary"] = rising_summary

            # Get MC interpretation
            mc_sign = birth_chart.get("angles", {}).get("midheaven", {}).get("sign")
            if mc_sign:
                self.logger.debug(f"Generating MC interpretation for {mc_sign}")
                mc_interp = self._get_house_interpretation(10, mc_sign)
                interpretation["mc_summary"] = mc_interp
                self.logger.debug("MC interpretation generated")

            # Get IC interpretation
            ic_sign = birth_chart.get("angles", {}).get("imum_coeli", {}).get("sign")
            if ic_sign:
                self.logger.debug(f"Generating IC interpretation for {ic_sign}")
                ic_interp = self._get_house_interpretation(4, ic_sign)
                interpretation["ic_summary"] = ic_interp
                self.logger.debug("IC interpretation generated")

            # Get DSC interpretation
            dsc_sign = birth_chart.get("angles", {}).get("descendant", {}).get("sign")
            if dsc_sign:
                self.logger.debug(f"Generating DSC interpretation for {dsc_sign}")
                dsc_interp = self._get_house_interpretation(7, dsc_sign)
                interpretation["dsc_summary"] = dsc_interp
                self.logger.debug("DSC interpretation generated")

            # --- End Angle Interpretation ---

            # Get chart shape
            chart_shape_analysis = self._analyze_chart_shape(birth_chart)
            interpretation["chart_shape"] = chart_shape_analysis

            # NEW: Generate structured sections and display order
            structured_sections, display_order = self._generate_structured_sections(birth_chart, level, 
                element_balance, modality_balance, simple_patterns, pattern_interpretations)
            interpretation["structured_sections"] = structured_sections
            interpretation["display_order"] = display_order

            self.logger.info("Interpretation generation completed successfully")
            return interpretation
        except Exception as e:
            self.logger.error(
                f"Error generating interpretation: {str(e)}",
                exc_info=True)
            return {
                "error": f"Error generating interpretation: {str(e)}",
                "success": False
            }

    def _generate_structured_sections(
            self,
            birth_chart: Dict,
            level: str,
            element_balance: Dict,
            modality_balance: Dict,
            simple_patterns: List[Dict],
            patterns: List[Dict]) -> Tuple[Dict, List[str]]:
        """Generate structured sections for modular rendering.
        
        Args:
            birth_chart: Birth chart data
            level: Level of detail
            element_balance: Element balance data
            modality_balance: Modality balance data
            simple_patterns: Simple patterns data
            patterns: Complex patterns data
            
        Returns:
            Tuple of (structured_sections, display_order)
        """
        # Create structured sections
        structured_sections = {}
        
        # Define display order (can be adjusted as needed)
        display_order = [
            "overview",
            "element_balance",
            "modality_balance",
            "stelliums",
            "house_emphasis",
            "chart_patterns",
            "retrograde_planets",
            "sign_distribution",
            "angles"
        ]
        
        # Create sections
        
        # Overview Section
        structured_sections["overview"] = {
            "title": "Birth Chart Interpretation",
            "content": "This chart represents your cosmic blueprint at birth, revealing your unique traits, strengths, and life themes."
        }
        
        # Element Balance Section
        if element_balance:
            # Extract text from element_balance interpretation
            element_content = ""
            if "interpretation" in element_balance:
                element_content = element_balance["interpretation"]
            
            structured_sections["element_balance"] = {
                "title": "Element Balance",
                "content": element_content,
                "data": element_balance
            }
        
        # Modality Balance Section
        if modality_balance:
            # Extract text from modality_balance interpretation
            modality_content = ""
            if "interpretation" in modality_balance:
                modality_content = modality_balance["interpretation"]
            
            structured_sections["modality_balance"] = {
                "title": "Modality Balance",
                "content": modality_content,
                "data": modality_balance
            }
        
        # Stelliums Section
        stellium_patterns = [p for p in simple_patterns if p.get("type") == "stellium"]
        if stellium_patterns:
            stellium_content = ""
            for pattern in stellium_patterns:
                if pattern.get("interpretation"):
                    stellium_content += f"**{pattern['sign']} Stellium**: {pattern['interpretation']}\n\n"
            
            structured_sections["stelliums"] = {
                "title": "Planetary Concentrations",
                "content": stellium_content,
                "data": stellium_patterns
            }
        
        # House Emphasis Section
        house_patterns = [p for p in simple_patterns if p.get("type") == "house_emphasis"]
        if house_patterns:
            house_content = ""
            for pattern in house_patterns:
                if pattern.get("interpretation"):
                    house_content += f"**House {pattern['house']} Emphasis**: {pattern['interpretation']}\n\n"
            
            structured_sections["house_emphasis"] = {
                "title": "House Emphasis",
                "content": house_content,
                "data": house_patterns
            }
        
        # Chart Patterns Section
        if patterns:
            patterns_content = ""
            for pattern in patterns:
                if pattern.get("interpretation"):
                    patterns_content += f"**{pattern['type']}**: {pattern['interpretation']}\n\n"
            
            structured_sections["chart_patterns"] = {
                "title": "Chart Patterns",
                "content": patterns_content,
                "data": patterns
            }
        
        # Retrograde Planets Section
        retrograde_planets = [
            planet_name for planet_name, planet_data in birth_chart.get("planets", {}).items()
            if planet_data.get("retrograde")
        ]
        
        if retrograde_planets:
            retrograde_content = f"You have {len(retrograde_planets)} retrograde planets: {', '.join(retrograde_planets)}. "
            retrograde_content += "Retrograde planets represent energies that are internalized and often require deeper reflection."
            
            structured_sections["retrograde_planets"] = {
                "title": "Retrograde Planets",
                "content": retrograde_content,
                "data": {"planets": retrograde_planets}
            }
        
        # Sign Distribution Section
        sign_distribution = {}
        for planet_name, planet_data in birth_chart.get("planets", {}).items():
            sign = planet_data.get("sign")
            if sign:
                if sign not in sign_distribution:
                    sign_distribution[sign] = []
                sign_distribution[sign].append(planet_name)
        
        structured_sections["sign_distribution"] = {
            "title": "Sign Distribution",
            "content": "Distribution of planets across zodiac signs.",
            "data": sign_distribution
        }
        
        # Angles Section
        angles_content = ""
        angles = birth_chart.get("angles", {})
        
        if angles.get("ascendant", {}).get("sign"):
            angles_content += f"**Ascendant in {angles['ascendant']['sign']}**: {self._get_rising_sign_summary(angles['ascendant']['sign'])}\n\n"
        
        if angles.get("midheaven", {}).get("sign"):
            angles_content += f"**Midheaven in {angles['midheaven']['sign']}**: {self._get_house_interpretation(10, angles['midheaven']['sign'])}\n\n"
        
        if angles.get("descendant", {}).get("sign"):
            angles_content += f"**Descendant in {angles['descendant']['sign']}**: {self._get_house_interpretation(7, angles['descendant']['sign'])}\n\n"
        
        if angles.get("imum_coeli", {}).get("sign"):
            angles_content += f"**Imum Coeli in {angles['imum_coeli']['sign']}**: {self._get_house_interpretation(4, angles['imum_coeli']['sign'])}\n\n"
        
        structured_sections["angles"] = {
            "title": "Important Angles",
            "content": angles_content,
            "data": angles
        }
        
        # Filter out any empty sections and reorder
        final_display_order = [section for section in display_order if section in structured_sections]
        
        return structured_sections, final_display_order

    def _generate_planet_interpretations(
            self,
            birth_chart: Dict,
            level: str = "basic") -> List[Dict]:
        """Generate interpretations for planets in the birth chart.

        Args:
            birth_chart: Birth chart data
            level: Level of detail for interpretations

        Returns:
            List of dictionaries containing planet interpretations
        """
        self.logger.debug(f"Generating {level} planet interpretations")
        planet_interpretations = []

        # Process planets (handling both dictionary and list formats)
        planets_data = birth_chart.get("planets", {})

        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                sign = planet_data.get("sign")
                house = planet_data.get("house")
                retrograde = planet_data.get("retrograde", False)

                if not sign or house is None:
                    continue

                # Generate interpretation
                interpretation = self._get_planet_interpretation(
                    planet_name, sign, house, retrograde)

                planet_interpretations.append({
                    "planet": planet_name,
                    "sign": sign,
                    "house": house,
                    "retrograde": retrograde,
                    "interpretation": interpretation
                })
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                name = planet.get("name")
                sign = planet.get("sign")
                house = planet.get("house")
                retrograde = planet.get("retrograde", False)

                if not name or not sign or house is None:
                    continue

                # Generate interpretation
                interpretation = self._get_planet_interpretation(
                    name, sign, house, retrograde)

                planet_interpretations.append({
                    "planet": name,
                    "sign": sign,
                    "house": house,
                    "retrograde": retrograde,
                    "interpretation": interpretation
                })

        self.logger.debug(
            f"Generated {len(planet_interpretations)} planet interpretations")
        return planet_interpretations

    def _get_planet_interpretation(
            self,
            planet: str,
            sign: str,
            house: int,
            retrograde: bool = False) -> str:
        """Generate interpretation for a planet in a sign and house using structured data.

        Args:
            planet: Planet name
            sign: Zodiac sign
            house: House number
            retrograde: Whether the planet is retrograde

        Returns:
            Interpretation text
        """
        self.logger.debug(
            f"Generating interpretation for {planet} in {sign} in the {house}th House using structured data")

        # Normalize inputs
        planet_lower = planet.lower()
        sign_lower = sign.lower()
        house_str = str(house)

        # --- Fetch data from caches/structured_data with fallbacks ---
        planet_data = self._planet_cache.get(planet_lower, {})
        sign_data = self._sign_cache.get(sign_lower, {})
        house_data = self._house_cache.get(house_str, {})
        dignities_data = self.structured_data.get("dignities", {})
        descriptions_data = self.structured_data.get("descriptions", {})

        # --- Planet in Sign Interpretation (using migrated data) ---
        level = "basic"  # Assuming basic for now, can be passed as arg later

        # --- Special handling for Sun/Moon descriptions ---
        if planet_lower == 'sun':
            sun_desc = descriptions_data.get(sign_lower, {}).get('sun_sign')
            if sun_desc:
                planet_sign_interp = sun_desc
                self.logger.debug(
                    f"Using dedicated sun_sign description for Sun in {sign}")
            else:
                # Fallback if specific sun description is missing
                self.logger.warning(
                    f"No dedicated sun_sign description found for {sign} in descriptions.json. Building generic.")
                planet_core = planet_data.get(
                    "description", f"The core energy of {planet.capitalize()}")
                sign_keywords = sign_data.get("keywords", [sign_lower])
                sign_keyword1 = sign_keywords[0] if sign_keywords else ""
                sign_keyword2 = sign_keywords[1] if len(sign_keywords) > 1 else sign_keyword1
                planet_sign_interp = f"{planet_core}. In the sign of {sign.capitalize()}, these energies are expressed through qualities like {sign_keyword1} and {sign_keyword2}."

        elif planet_lower == 'moon':
            moon_desc = descriptions_data.get(sign_lower, {}).get('moon_sign')
            if moon_desc:
                planet_sign_interp = moon_desc
                self.logger.debug(
                    f"Using dedicated moon_sign description for Moon in {sign}")
            else:
                # Fallback if specific moon description is missing
                self.logger.warning(
                    f"No dedicated moon_sign description found for {sign} in descriptions.json. Building generic.")
                # Specific fallback for Moon
                planet_core = planet_data.get(
                    "description", f"Your emotional nature")
                sign_keywords = sign_data.get("keywords", [sign_lower])
                sign_keyword1 = sign_keywords[0] if sign_keywords else ""
                sign_keyword2 = sign_keywords[1] if len(sign_keywords) > 1 else sign_keyword1
                planet_sign_interp = f"{planet_core} is analytical and practical. You process feelings through service and problem-solving. While you can be critical, your helpfulness and attention to detail are valuable. You need order and purpose in your emotional life."

        else:
            # --- Original logic for other planets ---
            sign_interpretations = planet_data.get("sign_interpretations", {})
            specific_sign_interp = sign_interpretations.get(
                level, {}).get(sign_lower)

            # Use specific interpretation if found, otherwise build a generic
            # one
            if specific_sign_interp:
                planet_sign_interp = specific_sign_interp
                self.logger.debug(
                    f"Using specific {level} interpretation for {planet} in {sign}")
            else:
                self.logger.warning(
                    f"No specific {level} interpretation found for {planet} in {sign} in planets.json. Building generic.")
                planet_core = planet_data.get(
                    "description", f"The energy of {planet.capitalize()}")
                sign_keywords = sign_data.get("keywords", [sign_lower])
                sign_keyword1 = sign_keywords[0] if sign_keywords else ""
                sign_keyword2 = sign_keywords[1] if len(sign_keywords) > 1 else sign_keyword1
                planet_sign_interp = f"{planet_core}. In the sign of {sign.capitalize()}, these energies manifest through qualities like {sign_keyword1} and {sign_keyword2}."

        # --- House area of life ---
        house_focus = house_data.get(
            "focus", f"the area of life associated with the {self._get_house_ordinal(house)} house")
        if not house_data:
            self.logger.warning(
                f"No data found for house {house} in houses.json")

        # Retrograde interpretation text (Consider moving to JSON later)
        retrograde_text = f" With {planet.capitalize()} retrograde, these energies are often internalized, prompting deeper reflection or unconventional expression." if retrograde else ""

        # --- Dignity Interpretation ---
        dignity_type = self._get_essential_dignity(planet_lower, sign_lower)
        dignity_interp_sentence = "" # Initialize dignity sentence
        if dignity_type != "peregrine":
            dignity_desc_full = dignities_data.get(
                dignity_type, {}).get("description", "") # Get full description
            if dignity_desc_full:
                # Format the full description
                formatted_desc = dignity_desc_full
                # Replace generic terms (case-insensitive for start of sentence)
                replacements = {
                    "a planet's": f"{planet.capitalize()}'s",
                    "a planet": f"{planet.capitalize()}",
                    "its home sign": f"its home sign {sign.capitalize()}", # Specific for domicile
                    "the planet's": f"{planet.capitalize()}'s",
                    "the planet": f"{planet.capitalize()}",
                }
                for generic, specific in replacements.items():
                    formatted_desc = formatted_desc.replace(generic, specific)
                    formatted_desc = formatted_desc.replace(generic.capitalize(), specific) # Handle start of sentence

                # Construct the interpretation sentence
                dignity_interp_sentence = f"In terms of essential dignity, {planet.capitalize()} is in {dignity_type.capitalize()} here. {formatted_desc}"
            else:
                self.logger.warning(
                    f"No description found for dignity '{dignity_type}' in dignities.json")
                # Fallback if description missing but dignity known
                dignity_interp_sentence = f"In terms of essential dignity, {planet.capitalize()} is in {dignity_type.capitalize()} here, which influences its expression."

        # --- Build Final Interpretation (Revised) ---
        # Format house number with correct ordinal
        house_ordinal = self._get_house_ordinal(house)

        interpretation_parts = [
            f"{planet.capitalize()} in {sign.capitalize()} in the {house_ordinal} House:",
            planet_sign_interp.rstrip(".") # Planet-in-Sign interpretation, remove trailing period if present
        ]
        if dignity_interp_sentence: # Add dignity interpretation if available
            interpretation_parts.append(dignity_interp_sentence)
            
        # Add house placement with improved wording
        interpretation_parts.append(f"Placed in the {house_ordinal} House, this influence manifests particularly in relation to {house_focus}.")
        
        if retrograde_text:
            interpretation_parts.append(retrograde_text.strip()) # Add retrograde text if applicable

        interpretation = " ".join(interpretation_parts) # Join all parts with spaces

        return interpretation # Return the combined string
        
    def _get_house_ordinal(self, house: int) -> str:
        """Return house number with appropriate ordinal suffix."""
        if house == 1:
            return "1st"
        elif house == 2:
            return "2nd"
        elif house == 3:
            return "3rd"
        else:
            return f"{house}th"

    def _generate_house_interpretations(
            self,
            birth_chart: Dict,
            level: str = "basic") -> List[Dict]:
        """Generate interpretations for houses in the birth chart.

        Args:
            birth_chart: Birth chart data
            level: Level of detail for interpretations

        Returns:
            List of dictionaries containing house interpretations
        """
        self.logger.debug(f"Generating {level} house interpretations")
        house_interpretations = []

        # Process houses (handling both dictionary and list formats)
        houses_data = birth_chart.get("houses", {})

        if isinstance(houses_data, dict):
            # Dictionary format (new)
            for house_num_str, house_data in houses_data.items():
                try:
                    house_num = int(house_num_str)
                    sign = house_data.get("sign")

                    if not sign:
                        continue

                    # Generate interpretation
                    interpretation = self._get_house_interpretation(
                        house_num, sign)

                    house_interpretations.append({
                        "house": house_num,
                        "sign": sign,
                        "interpretation": interpretation
                    })
                except (ValueError, TypeError):
                    self.logger.warning(
                        f"Invalid house number: {house_num_str}")
                    continue
        elif isinstance(houses_data, list):
            # List format (old)
            for house in houses_data:
                house_num = house.get("house_num")
                sign = house.get("sign")

                if house_num is None or not sign:
                    continue

                # Generate interpretation
                interpretation = self._get_house_interpretation(
                    house_num, sign)

                house_interpretations.append({
                    "house": house_num,
                    "sign": sign,
                    "interpretation": interpretation
                })

        self.logger.debug(
            f"Generated {len(house_interpretations)} house interpretations")
        return house_interpretations

    def _get_house_interpretation(self, house_num: int, sign: str) -> str:
        """Generate interpretation for a house with a specific sign on its cusp.

        Args:
            house_num: House number
            sign: Zodiac sign on the house cusp

        Returns:
            Interpretation text
        """
        self.logger.debug(
            f"Generating interpretation for House {house_num} with {sign} on cusp")

        # Normalize inputs
        sign_lower = sign.lower()
        house_str = str(house_num)

        # Get data from structured_data
        house_data = self.structured_data.get("houses", {}).get(house_str, {})
        sign_data = self.structured_data.get("signs", {}).get(sign_lower, {})

        # --- Get Specific Cusp Interpretation ---
        specific_interp = house_data.get(
            "cusp_sign_interpretations", {}).get(
            "basic", {}).get(sign_lower)

        if specific_interp:
            self.logger.debug(
                f"Using specific interpretation for House {house_num} cusp in {sign}")
            return f"House {house_num} ({sign.capitalize()} cusp): {specific_interp}"
        else:
            self.logger.warning(
                f"No specific cusp interpretation found for House {house_num} in {sign}. Building generic.")
            # --- Fallback to Generic Description ---
            house_focus = house_data.get("focus")
            if not house_focus:
                house_focus = f"matters associated with house {house_num}"
                self.logger.warning(
                    f"No focus found for House {house_num} in houses.json")

            sign_quality = sign_data.get("qualities", {}).get("general")
            if not sign_quality:
                sign_quality = sign_lower  # Use sign name as fallback
                self.logger.warning(
                    f"No general quality found for sign {sign} in signs.json")

            # Build interpretation using data from JSON
            interpretation = f"House {house_num} with {sign.capitalize()} on the cusp influences {house_focus}. "
            interpretation += f"This brings {sign_quality} qualities to this area of life."
        return interpretation

    def _generate_aspect_interpretations(
            self,
            birth_chart: Dict,
            level: str = "basic") -> List[Dict]:
        """Generate interpretations for aspects in the birth chart.

        Args:
            birth_chart: Birth chart data
            level: Level of detail for interpretations

        Returns:
            List of dictionaries containing aspect interpretations
        """
        self.logger.debug(f"Generating {level} aspect interpretations")
        aspect_interpretations = []

        # Get aspects from the birth chart
        aspects = birth_chart.get("aspects", [])

        for aspect in aspects:
            planet1 = aspect.get("planet1")
            planet2 = aspect.get("planet2")
            aspect_type = aspect.get("type")
            orb = aspect.get("orb", 0)

            if not planet1 or not planet2 or aspect_type is None:
                continue

            # Generate interpretation
            interpretation = self._get_aspect_interpretation(
                planet1, planet2, aspect_type, orb)

            if interpretation:
                aspect_interpretations.append({
                    "planet1": planet1,
                    "planet2": planet2,
                    "type": aspect_type,
                    "orb": orb,
                    "interpretation": interpretation
                })

        self.logger.debug(
            f"Generated {len(aspect_interpretations)} aspect interpretations")
        return aspect_interpretations

    def _get_aspect_interpretation(self,
                                   planet1: str,
                                   planet2: str,
                                   aspect_type: Union[int,
                                                      str],
                                   orb: float = 0) -> str:
        """Generate interpretation for an aspect between two planets.

        Args:
            planet1: First planet
            planet2: Second planet
            aspect_type: Type of aspect (0/conjunction, 60/sextile, 90/square, 120/trine, 180/opposition)
            orb: Orb of the aspect

        Returns:
            Interpretation text or None if aspect type is unknown.
        """
        self.logger.debug(
            f"Generating interpretation for {planet1}-{planet2} {aspect_type} aspect")

        # Normalize inputs
        planet1_lower = planet1.lower()
        planet2_lower = planet2.lower()
        # Ensure consistent ordering for lookup (e.g., sun_moon not moon_sun)
        sorted_planets = sorted([planet1_lower, planet2_lower])
        pair_key = f"{sorted_planets[0]}_{sorted_planets[1]}"
        # Use lowercase string key for cache lookup
        aspect_key = str(aspect_type).lower()

        # Get data from structured_data cache
        aspect_data = self._aspect_cache.get(aspect_key)
        planet1_data = self._planet_cache.get(planet1_lower, {})
        planet2_data = self._planet_cache.get(planet2_lower, {})

        if not aspect_data:
            self.logger.warning(
                f"Unknown aspect type: {aspect_type}. Skipping interpretation.")
            return None

        # --- Try Specific Pair Interpretation First ---
        specific_interp = aspect_data.get("specific_pairs", {}).get(pair_key)
        if specific_interp:
            self.logger.debug(
                f"Using specific interpretation for {pair_key} {aspect_key} aspect")
            interpretation_core = specific_interp
        else:
            # --- Fallback to Generic Interpretation ---
            self.logger.debug(
                f"No specific interpretation found for {pair_key} {aspect_key}. Building generic.")
            aspect_name = aspect_data.get("name", aspect_key.capitalize())
            aspect_keywords = aspect_data.get("keywords", [])
            aspect_action = aspect_keywords[0] if aspect_keywords else aspect_data.get(
                "nature", "influences")
            planet1_keyword = planet1_data.get("keywords", [planet1_lower])[0]
            planet2_keyword = planet2_data.get("keywords", [planet2_lower])[0]

            interpretation_core = (
                f"{planet1.capitalize()} {aspect_name} {planet2.capitalize()}: "
                f"This aspect {aspect_action} the themes of {planet1_keyword} ({planet1.capitalize()}) "
                f"and {planet2_keyword} ({planet2.capitalize()}).")

        # --- Add Orb Significance ---
        orb_text = ""
        defined_orb = aspect_data.get("orb", 8)  # Default to 8 if not defined
        if orb < (defined_orb / 4.0):
            orb_text = f" With a tight orb of {orb:.1f}°, its influence is particularly direct and significant."
        elif orb > (defined_orb * 0.85):  # If close to max orb
            orb_text = f" With a wider orb of {orb:.1f}°, its influence may be less immediate but still relevant."

        # Combine core interpretation with orb text
        interpretation = f"{interpretation_core}{orb_text}"

        return interpretation.strip()

    def _generate_overall_interpretation(
            self,
            birth_chart: Dict,
            level: str = "basic") -> str:
        """Generate an overall interpretation of the birth chart.

        Args:
            birth_chart: Birth chart data
            level: Level of detail for the interpretation

        Returns:
            Overall interpretation as HTML
        """
        self.logger.debug(f"Generating {level} overall interpretation")

        # Get element and modality balances
        element_balance = self._analyze_simple_element_balance(birth_chart)
        modality_balance = self._analyze_simple_modality_balance(birth_chart)

        # Find chart patterns
        patterns = self._analyze_complex_patterns(birth_chart)
        
        # Find simple patterns (stelliums, house emphasis)
        simple_patterns = self._analyze_simple_patterns(birth_chart)
        
        # Get combinations
        combinations = self._analyze_combinations(birth_chart)
        
        # Get chart shape
        chart_shape = self._analyze_chart_shape(birth_chart)
        
        # Get angles interpretations
        mc_sign = birth_chart.get("angles", {}).get("midheaven", {}).get("sign")
        ic_sign = birth_chart.get("angles", {}).get("imum_coeli", {}).get("sign")
        dsc_sign = birth_chart.get("angles", {}).get("descendant", {}).get("sign")
        
        mc_summary = ""
        ic_summary = ""
        dsc_summary = ""
        
        if mc_sign:
            mc_house_data = self._house_cache.get("10", {})
            mc_sign_specific = mc_house_data.get(mc_sign.lower(), "")
            mc_summary = mc_sign_specific or f"House 10 with {mc_sign} on the cusp influences Career and public life"
            
        if ic_sign:
            ic_house_data = self._house_cache.get("4", {})
            ic_sign_specific = ic_house_data.get(ic_sign.lower(), "")
            ic_summary = ic_sign_specific or f"House 4 with {ic_sign} on the cusp influences Home and emotional foundation"
            
        if dsc_sign:
            dsc_house_data = self._house_cache.get("7", {})
            dsc_sign_specific = dsc_house_data.get(dsc_sign.lower(), "")
            dsc_summary = dsc_sign_specific or f"House 7 with {dsc_sign} on the cusp influences Relationships and partnerships"
            
        # Get rising sign interpretation
        asc_sign = birth_chart.get("angles", {}).get("ascendant", {}).get("sign")
        asc_interpretation = ""
        if asc_sign:
            asc_interpretation = self._get_rising_sign_summary(asc_sign)
        
        # Generate planet interpretations
        planet_interpretations = self._generate_planet_interpretations(birth_chart, level)
        self.logger.debug(f"Generated {len(planet_interpretations)} planet interpretations")
        
        # Generate house interpretations
        house_interpretations = self._generate_house_interpretations(birth_chart, level)
        self.logger.debug(f"Generated {len(house_interpretations)} house interpretations")
        
        # Generate aspect interpretations  
        aspect_interpretations = self._generate_aspect_interpretations(birth_chart, level)
        self.logger.debug(f"Generated {len(aspect_interpretations)} aspect interpretations")
            
        # Prepare template variables
        template_vars = {
            "birth_chart": birth_chart,
            "planets": planet_interpretations,
            "houses": house_interpretations,
            "aspects": aspect_interpretations,
            "patterns": patterns,
            "simple_patterns": simple_patterns,
            "element_balance": element_balance,
            "modality_balance": modality_balance,
            "combinations": combinations,
            "chart_shape": chart_shape,
            "mc_summary": mc_summary,
            "ic_summary": ic_summary,
            "dsc_summary": dsc_summary,
            "asc_interpretation": asc_interpretation
        }
        
        # Debug some key template variables
        self.logger.debug(f"Sun in birth chart: {birth_chart.get('planets', {}).get('Sun', {}).get('sign', 'Not found')}")
        self.logger.debug(f"Number of planets: {len(planet_interpretations)}")
        self.logger.debug(f"Number of patterns: {len(patterns)}")
        
        try:
            # Render the template
            template = self.jinja_env.get_template("overall_interpretation.txt.j2")
            markdown_interpretation = template.render(**template_vars)
            
            # Convert markdown to HTML with extras for better formatting
            html_interpretation = markdown2.markdown(
                markdown_interpretation,
                extras=[
                    'break-on-newline',
                    'tables',
                    'header-ids',
                    'fenced-code-blocks'
                ]
            )
            
            self.logger.debug(f"Generated overall interpretation as HTML: {html_interpretation[:50]}...")
            return html_interpretation
        except Exception as e:
            self.logger.error(f"Error rendering overall interpretation template: {str(e)}", exc_info=True)
            
            # Fallback to old method if template rendering fails
            interpretation_parts = []
            
            # Add element balance interpretation
            if element_balance and "interpretation" in element_balance:
                interpretation_parts.append(element_balance["interpretation"])
                
            # Add modality balance interpretation
            if modality_balance and "interpretation" in modality_balance:
                interpretation_parts.append(modality_balance["interpretation"])
                
            # Add aspect balance interpretation
            aspects = birth_chart.get("aspects", [])
            harmonious_count = 0
            challenging_count = 0
            
            for aspect in aspects:
                aspect_type_str = str(aspect.get("type")).lower()
                aspect_data = self._aspect_cache.get(aspect_type_str, {})
                nature = aspect_data.get("nature")
                
                if nature == "harmonious":
                    harmonious_count += 1
                elif nature == "challenging":
                    challenging_count += 1
                    
            aspect_balance_texts = self.structured_data.get(
                "interpretation_patterns", {}).get(
                "aspect_balance", {})
            balance_text = ""
            if harmonious_count == 0 and challenging_count == 0:
                balance_text = aspect_balance_texts.get(
                    "balanced", "")
            elif harmonious_count > challenging_count * 1.5:
                balance_text = aspect_balance_texts.get("harmonious_dominant", "")
            elif challenging_count > harmonious_count * 1.5:
                balance_text = aspect_balance_texts.get("challenging_dominant", "")
            else:
                balance_text = aspect_balance_texts.get("balanced", "")
                
            if balance_text:
                interpretation_parts.append(balance_text)
            else:
                self.logger.warning(
                    "Could not find aspect balance text in interpretation_patterns.json")
                    
            # Add summary sentence
            interpretation_parts.append(
                "This natal chart represents a unique combination of energies and potential that unfolds throughout your life."
            )
            
            # Combine all parts and convert to HTML
            markdown_interpretation = " ".join(interpretation_parts)
            html_interpretation = markdown2.markdown(
                markdown_interpretation,
                extras=[
                    'break-on-newline',
                    'tables',
                    'header-ids',
                    'fenced-code-blocks'
                ]
            )
            
            self.logger.debug(
                f"Generated fallback overall interpretation as HTML: {html_interpretation[:50]}...")
            return html_interpretation

    def _calculate_planetary_positions(self, date: Datetime) -> dict:
        """Calculate positions of planets using flatlib."""
        # This method should not be used anymore
        logger.warning(
            "_calculate_planetary_positions was called but should not be used")
        return {}

    def _calculate_house_cusps(
            self,
            date: Datetime,
            latitude: float,
            longitude: float) -> dict:
        """Calculate house cusps."""
        # This method should not be used anymore
        logger.warning(
            "_calculate_house_cusps was called but should not be used")
        return {}

    def _convert_planet_position(
            self, planet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert planet position data from the birth chart service."""
        return planet_data  # Already in the correct format

    def _convert_house_cusp(
            self, house_data: Dict[str, Any]) -> Dict[str, Any]:
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
        # This is a simplified version - actual house calculation depends on
        # house system
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
            planet_data = self.structured_data.get(
                "planets", {}).get(name.lower(), {})
            if planet_data:
                planet_quality = planet_data.get("qualities", "")

            sign_data = self.structured_data.get(
                "signs", {}).get(sign.lower(), {})
            if sign_data:
                sign_quality = sign_data.get("qualities", "")

            house_data = self.structured_data.get(
                "houses", {}).get(str(house), {})
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

    def _get_stellium_interpretation(
            self, sign: str, planets: List[str]) -> str:
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
            f"A chart with dominant {modality.title()} energy indicates a {modality_char}.")

    def _find_yod(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Yod (Finger of God) patterns in the aspects."""
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
                            match = False
                            if quincunx2["planet1"].lower(
                            ) == third_planet.lower():
                                if quincunx2["planet2"].lower() == planet2:
                                    match = True
                            elif quincunx2["planet2"].lower() == third_planet.lower():
                                if quincunx2["planet1"].lower() == planet2:
                                    match = True

                            if match:
                                # Found a Yod
                                planets = sorted(
                                    [planet1, planet2, third_planet.lower()])
                                key = "-".join(planets)

                                if key not in seen_combinations:
                                    seen_combinations.add(key)
                                    yods.append(
                                        {"planets": planets, "apex": third_planet.lower()})

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
            return "domicile"  # Changed from "rulership" to match dignities.json

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

    def _get_compatibility_interpretation(
            self, planet1: str, planet2: str) -> str:
        """Generate an interpretation of the compatibility between two planets."""
        # Normalize planet names
        planet1 = planet1.lower()
        planet2 = planet2.lower()

        # These pairs represent classic harmonic relationships in astrology
        harmonious_pairs = [
            # Same element pairs
            {"planets": ["sun", "mars"], "reason": "both fiery and active"},
            {"planets": ["sun", "jupiter"],
                "reason": "both expansive and warm"},
            {"planets": ["moon", "venus"],
                "reason": "both receptive and nurturing"},
            {"planets": ["moon", "neptune"],
                "reason": "both intuitive and sensitive"},
            {
                "planets": ["mercury", "uranus"],
                "reason": "both intellectual and quick-thinking",
            },
            {"planets": ["venus", "neptune"],
                "reason": "both romantic and idealistic"},
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
            {"planets": ["neptune", "moon"],
                "reason": "both dreamy and empathic"},
            {"planets": ["pluto", "mars"],
                "reason": "both intense and focused"},
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
                # For other element combinations, we'll skip element
                # compatibility
                pass

            # Create a general interpretation
            return f"{planet1.capitalize()} ({p1_qualities['nature']}) interacts with {planet2.capitalize()} ({p2_qualities['nature']}). {element_compatibility}"

        # Default return for unlisted planetary pairs
        return ""

    def _get_sign_element(self, sign: str) -> str:
        """Get the element associated with a zodiac sign.

        Args:
            sign: Zodiac sign name

        Returns:
            Element name (fire, earth, air, water)
        """
        sign = sign.lower() if sign else ""

        fire_signs = ["aries", "leo", "sagittarius"]
        earth_signs = ["taurus", "virgo", "capricorn"]
        air_signs = ["gemini", "libra", "aquarius"]
        water_signs = ["cancer", "scorpio", "pisces"]

        if sign in fire_signs:
            return "fire"
        elif sign in earth_signs:
            return "earth"
        elif sign in air_signs:
            return "air"
        elif sign in water_signs:
            return "water"
        else:
            self.logger.warning(
                f"Unknown sign for element determination: {sign}")
            return "unknown"

    def _get_sign_modality(self, sign: str) -> str:
        """Get the modality associated with a zodiac sign.

        Args:
            sign: Zodiac sign name

        Returns:
            Modality name (cardinal, fixed, mutable)
        """
        sign = sign.lower() if sign else ""

        cardinal_signs = ["aries", "cancer", "libra", "capricorn"]
        fixed_signs = ["taurus", "leo", "scorpio", "aquarius"]
        mutable_signs = ["gemini", "virgo", "sagittarius", "pisces"]

        if sign in cardinal_signs:
            return "cardinal"
        elif sign in fixed_signs:
            return "fixed"
        elif sign in mutable_signs:
            return "mutable"
        else:
            self.logger.warning(
                f"Unknown sign for modality determination: {sign}")
            return "unknown"

    def _get_rising_sign_summary(self, rising_sign: str) -> str:
        """Generate a summary based on the rising sign (Ascendant) using structured data.

        Args:
            rising_sign: The rising sign

        Returns:
            Summary text
        """
        self.logger.debug(f"Generating rising sign summary for: {rising_sign}")

        rising_sign_lower = rising_sign.lower()
        description = ""

        # Fetch summary from structured data
        try:
            description = self.structured_data.get(
                "descriptions",
                {}).get(
                rising_sign_lower,
                {}).get(
                "rising_sign",
                "")
            if description:
                self.logger.debug(
                    f"Found rising sign summary in structured data for {rising_sign}")
            else:
                self.logger.warning(
                    f"No rising_sign description found for {rising_sign} in descriptions.json")
        except AttributeError:
            self.logger.error(
                f"Error accessing rising sign description for {rising_sign} in structured data.")

        # Fallback if no description found
        if not description:
            description = f"Your {rising_sign.capitalize()} Ascendant influences your outward persona and first impressions. It shapes how you meet the world and begin new experiences."
            self.logger.debug(
                f"Using default fallback rising sign description for {rising_sign}")

        return description

    def _analyze_simple_element_balance(self, birth_chart: Dict) -> Dict:
        """Analyze the element balance in a birth chart.

        Args:
            birth_chart: Birth chart data

        Returns:
            Dictionary containing element balance information
        """
        self.logger.debug("Analyzing element balance")

        # Initialize element counts and planet groupings
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        element_planets = {"fire": [], "earth": [], "air": [], "water": []}

        # Process planets (handling both dictionary and list formats)
        planets_data = birth_chart.get("planets", {})

        # Define points to exclude (non-planetary objects)
        excluded_points = ["ascendant", "midheaven", "descendant", "ic", "north_node", "south_node"]

        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC, and Nodes
                if planet_name.lower() in excluded_points:
                    continue

                sign = planet_data.get("sign", "").lower()
                element = self._get_sign_element(sign)

                if element in elements:
                    elements[element] += 1
                    element_planets[element].append(planet_name)
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC, and Nodes
                if planet.get("name", "").lower() in excluded_points:
                    continue

                sign = planet.get("sign", "").lower()
                element = self._get_sign_element(sign)

                if element in elements:
                    elements[element] += 1
                    element_planets[element].append(planet.get("name"))

        # Calculate percentages
        total_planets = sum(elements.values())
        percentages = {}

        if total_planets > 0:
            for element, count in elements.items():
                percentages[element] = round((count / total_planets) * 100, 2)

        # Determine dominant and lacking elements
        sorted_elements = sorted(
            elements.items(),
            key=lambda x: x[1],
            reverse=True)
        dominant = sorted_elements[0][0] if sorted_elements[0][1] > 0 else None
        lacking = [
            element for element,
            count in elements.items() if count <= 1]

        # Generate interpretation
        interpretation = self._generate_element_balance_interpretation(
            dominant, lacking, percentages)

        # Prepare result
        result = {
            "counts": elements,
            "percentages": percentages,
            "dominant": dominant,
            "lacking": lacking,
            "planets": element_planets,
            "interpretation": interpretation
        }

        self.logger.debug(f"Element balance analysis: {result['counts']}")
        return result

    def _generate_element_balance_interpretation(
            self, dominant: str, lacking: List[str], percentages: Dict[str, float]) -> str:
        """Generate an interpretation of the element balance using structured data.

        Args:
            dominant: Dominant element
            lacking: List of lacking elements
            percentages: Element percentages

        Returns:
            Interpretation text
        """
        interpretation_parts = []
        patterns_data = self.structured_data.get("interpretation_patterns", {})
        elemental_patterns = patterns_data.get("elemental_patterns", {})
        element_emphasis_patterns = patterns_data.get("element_emphasis", {})

        # Describe dominant element
        if dominant:
            percentage = round(percentages[dominant])
            # Use detailed description if emphasis is strong (e.g., > 40%),
            # otherwise concise
            if percentage > 40 and f"{dominant}_dominant" in element_emphasis_patterns:
                desc = element_emphasis_patterns[f"{dominant}_dominant"].get(
                    "description", "")
                interpretation_parts.append(
                    f"A {dominant.capitalize()} dominant chart occurs when a significant number of planets are positioned in {dominant} signs. {desc}")
            elif f"{dominant}_dominant" in elemental_patterns:
                desc = elemental_patterns[f"{dominant}_dominant"].get(
                    "description", f"a focus on {dominant} qualities.")
                interpretation_parts.append(
                    f"{desc}")
            else:
                interpretation_parts.append(
                    f"Your chart shows a strong emphasis on {dominant} qualities.")  # Fallback
                self.logger.warning(
                    f"No description found for dominant element {dominant} in interpretation_patterns.json")

        # Describe lacking elements
        if lacking:
            # Use detailed description if element is very lacking (e.g., 0
            # planets)
            lacking_elements_str = []
            for element in lacking:
                # Get count via percentage (approximate)
                count = percentages.get(element, 0)
                if count == 0 and f"{element}_lacking" in element_emphasis_patterns:
                    desc = element_emphasis_patterns[f"{element}_lacking"].get(
                        "description", "")
                    lacking_elements_str.append(
                        f"A chart lacking {element.capitalize()} energy creates a natural challenge in accessing qualities like {self._get_element_keywords_simple(element)[0]}. {desc}")
                elif f"{element}_lacking" in elemental_patterns:
                    desc = elemental_patterns[f"{element}_lacking"].get(
                        "description", f"potential challenges related to {element} qualities.")
                    lacking_elements_str.append(
                        f"{desc}")
                else:
                    lacking_elements_str.append(
                        f"Your chart shows limited {element} energy, which may create challenges in accessing qualities like {self._get_element_keywords_simple(element)[0]}.")
                    self.logger.warning(
                        f"No description found for lacking element {element} in interpretation_patterns.json")
            if lacking_elements_str:
                interpretation_parts.extend(lacking_elements_str)

        # Note balance if neither dominant nor lacking elements
        if not dominant and not lacking:
            interpretation_parts.append(
                "Your chart shows a relatively balanced distribution of elements, "
                "suggesting versatility in approaching life through different modes of expression.")

        return " ".join(interpretation_parts)

    def _analyze_simple_modality_balance(self, birth_chart: Dict) -> Dict:
        """Analyze the modality balance in a birth chart.

        Args:
            birth_chart: Birth chart data

        Returns:
            Dictionary containing modality balance information
        """
        self.logger.debug("Analyzing modality balance")
        # Initialize modality counts and planet groupings
        modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
        modality_planets = {"cardinal": [], "fixed": [], "mutable": []}

        # Process planets (handling both dictionary and list formats)
        planets_data = birth_chart.get("planets", {})

        # Define points to exclude (non-planetary objects)
        excluded_points = ["ascendant", "midheaven", "descendant", "ic", "north_node", "south_node"]

        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC, and Nodes
                if planet_name.lower() in excluded_points:
                    continue

                sign = planet_data.get("sign", "").lower()
                modality = self._get_sign_modality(sign)

                if modality in modalities:
                    modalities[modality] += 1
                    modality_planets[modality].append(planet_name)
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC, and Nodes
                if planet.get("name", "").lower() in excluded_points:
                    continue

                sign = planet.get("sign", "").lower()
                modality = self._get_sign_modality(sign)

                if modality in modalities:
                    modalities[modality] += 1
                    modality_planets[modality].append(planet.get("name"))

        # Calculate percentages (Moved outside elif)
        total_planets = sum(modalities.values())
        percentages = {}

        if total_planets > 0:
            for modality, count in modalities.items():
                percentages[modality] = round((count / total_planets) * 100, 2)
        else:  # Handle case where no planets were counted
            percentages = {m: 0.0 for m in modalities}

        # Determine dominant and lacking modalities
        dominant = None
        lacking = []  # Initialize lacking
        if total_planets > 0:
            sorted_modalities = sorted(
                modalities.items(),
                key=lambda x: x[1],
                reverse=True)
            # Added check if sorted_modalities is not empty
            if sorted_modalities and sorted_modalities[0][1] > 0:
                dominant = sorted_modalities[0][0]
            lacking = [modality for modality,
                       count in modalities.items() if count <= 1]

        # Generate interpretation
        interpretation = self._generate_modality_balance_interpretation(
            dominant, lacking, percentages)

        # Prepare result
        result = {
            "counts": modalities,
            "percentages": percentages,
            "dominant": dominant,
            "lacking": lacking,
            "planets": modality_planets,
            "interpretation": interpretation
        }

        self.logger.debug(f"Modality balance analysis: {result['counts']}")
        return result

    def _generate_modality_balance_interpretation(
            self, dominant: str, lacking: List[str], percentages: Dict[str, float]) -> str:
        """Generate an interpretation of the modality balance using structured data.

        Args:
            dominant: Dominant modality
            lacking: List of lacking modalities
            percentages: Modality percentages

        Returns:
            Interpretation text
        """
        interpretation_parts = []
        patterns_data = self.structured_data.get("interpretation_patterns", {})
        modality_patterns = patterns_data.get("modality_patterns", {})
        modality_emphasis_patterns = patterns_data.get("modality_emphasis", {})

        # Describe dominant modality
        if dominant:
            percentage = round(percentages[dominant])
            # Use detailed description if emphasis is strong (e.g., > 40%),
            # otherwise concise
            if percentage > 40 and f"{dominant}_dominant" in modality_emphasis_patterns:
                desc = modality_emphasis_patterns[f"{dominant}_dominant"].get(
                    "description", "")
                interpretation_parts.append(
                    f"A {dominant.capitalize()} dominant chart occurs when a significant number of planets (typically four or more) are positioned in the {dominant} signs. {desc}")
            elif f"{dominant}_dominant" in modality_patterns:
                desc = modality_patterns[f"{dominant}_dominant"].get(
                    "description", f"a focus on {dominant} qualities.")
                interpretation_parts.append(
                    f"{desc}")
            else:
                interpretation_parts.append(
                    f"Your chart shows a strong emphasis on {dominant} qualities, suggesting a natural tendency toward {self._get_modality_keywords(dominant)[0]}.")  # Fallback
                self.logger.warning(
                    f"No description found for dominant modality {dominant} in interpretation_patterns.json")

        # Describe lacking modalities
        if lacking:
            lacking_modalities_str = []
            for modality in lacking:
                # Get count via percentage (approximate)
                count = percentages.get(modality, 0)
                if count == 0 and f"{modality}_lacking" in modality_emphasis_patterns:
                    desc = modality_emphasis_patterns[f"{modality}_lacking"].get(
                        "description", "")
                    lacking_modalities_str.append(
                        f"A chart lacking {modality.capitalize()} energy (no planets or only one planet in {modality} signs) creates a natural challenge in {self._get_modality_keywords(modality)[0]}. {desc}")
                elif f"{modality}_lacking" in modality_patterns:
                    desc = modality_patterns[f"{modality}_lacking"].get(
                        "description", f"potential challenges related to {modality} qualities.")
                    lacking_modalities_str.append(
                        f"{desc}")
                else:
                    lacking_modalities_str.append(
                        f"Your chart shows limited {modality} energy, which may create challenges in {self._get_modality_keywords(modality)[0]}.")
                    self.logger.warning(
                        f"No description found for lacking modality {modality} in interpretation_patterns.json")
            if lacking_modalities_str:
                interpretation_parts.extend(lacking_modalities_str)

        # Note balance if neither dominant nor lacking modalities
        if not dominant and not lacking:
            interpretation_parts.append(
                "Your chart shows a relatively balanced distribution of modalities, "
                "suggesting versatility in how you approach initiation, stabilization, and adaptation.")

        return " ".join(interpretation_parts)
        
    def _get_modality_keywords(self, modality: str) -> List[str]:
        """Get keywords for a modality. Helper for interpretation generation."""
        keywords = {
            "cardinal": ["initiating action", "leadership", "starting new things"],
            "fixed": ["stabilizing", "persisting", "maintaining"],
            "mutable": ["adapting", "flexibility", "versatility"]
        }
        return keywords.get(modality.lower(), ["expressing energy"])

    def _analyze_simple_patterns(self, birth_chart: Dict) -> List[Dict]:
        """Analyze birth chart for simple astrological patterns like stelliums.

        Args:
            birth_chart: Birth chart data

        Returns:
            List of dictionaries containing simple pattern information
        """
        self.logger.debug("Analyzing simple patterns")
        patterns = []

        # Analyze stelliums (3 or more planets in the same sign)
        sign_counts = {}
        sign_planets = {}
        # Also count planets per house for emphasis analysis
        house_counts = {str(i): 0 for i in range(1, 13)}
        house_planets = {str(i): [] for i in range(1, 13)}

        # Process planets (handling both dictionary and list formats)
        planets_data = birth_chart.get("planets", {})

        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC
                if planet_name.lower() in [
                        "ascendant", "midheaven", "descendant", "ic"]:
                    continue

                sign = planet_data.get("sign")
                if sign:
                    sign_lower = sign.lower()
                    sign_counts[sign_lower] = sign_counts.get(
                        sign_lower, 0) + 1

                    if sign_lower not in sign_planets:
                        sign_planets[sign_lower] = []
                    sign_planets[sign_lower].append(planet_name)

                # Count house placements
                house = planet_data.get("house")
                if house is not None:
                    house_str = str(house)
                    if house_str in house_counts:
                        house_counts[house_str] += 1
                        house_planets[house_str].append(planet_name)

        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC
                if planet.get(
                        "name",
                        "").lower() in [
                        "ascendant",
                        "midheaven",
                        "descendant",
                        "ic"]:
                    continue

                sign = planet.get("sign")
                if sign:
                    sign_lower = sign.lower()
                    sign_counts[sign_lower] = sign_counts.get(
                        sign_lower, 0) + 1

                    if sign_lower not in sign_planets:
                        sign_planets[sign_lower] = []
                    sign_planets[sign_lower].append(planet.get("name"))

                # Count house placements
                house = planet.get("house")
                if house is not None:
                    house_str = str(house)
                    if house_str in house_counts:
                        house_counts[house_str] += 1
                        house_planets[house_str].append(planet.get("name"))

        # Find stelliums
        for sign, count in sign_counts.items():
            if count >= 3:  # Consider 3+ planets a stellium
                # Fetch stellium template and description
                pattern_info = self.structured_data.get(
                    "interpretation_patterns", {}).get(
                    "stellium", {})
                description = pattern_info.get("description", "")
                template = pattern_info.get(
                    "interpretation_template",
                    "Stellium in {sign} ({count} planets). Amplifies {sign} qualities.")  # Fallback

                # Fetch sign keywords
                sign_data = self._sign_cache.get(sign, {})
                keywords_list = sign_data.get("keywords", [sign])
                # Use first 3 keywords
                keywords_str = ", ".join(keywords_list[:3])

                # Format interpretation
                planets_list_str = ", ".join(sign_planets[sign])
                interpretation_text = template.format(
                    sign=sign.capitalize(),
                    count=count,
                    planets_list=planets_list_str,
                    keywords=keywords_str,
                    description=description  # Consider adding only a snippet for brevity if needed
                )

                patterns.append({
                    "type": "stellium",
                    "sign": sign,
                    "planets": sign_planets[sign],
                    "count": count,
                    "interpretation": interpretation_text
                })

        # --- Analyze House Emphasis (3 or more planets in the same house) ---
        house_emphasis_data = self.structured_data.get("house_emphasis", {})
        house_num_map = {
            "1": "first_house", "2": "second_house", "3": "third_house",
            "4": "fourth_house", "5": "fifth_house", "6": "sixth_house",
            "7": "seventh_house", "8": "eighth_house", "9": "ninth_house",
            "10": "tenth_house", "11": "eleventh_house", "12": "twelfth_house"
        }

        for house_str, count in house_counts.items():
            if count >= 3:
                emphasis_key = house_num_map.get(house_str)
                if emphasis_key and emphasis_key in house_emphasis_data:
                    emphasis_info = house_emphasis_data[emphasis_key]
                    interpretation_text = emphasis_info.get(
                        "interpretation", "")
                    if interpretation_text:
                        patterns.append({
                            "type": "house_emphasis",
                            "house": int(house_str),
                            "planets": house_planets[house_str],
                            "count": count,
                            "interpretation": interpretation_text
                        })
                        self.logger.debug(
                            f"Found House {house_str} emphasis ({count} planets)")
                    else:
                        self.logger.warning(
                            f"No interpretation text found for {emphasis_key} in house_emphasis.json")
                else:
                    self.logger.warning(
                        f"No data found for {emphasis_key} (House {house_str}) in house_emphasis.json")

        self.logger.debug(
            f"Found {len(patterns)} simple patterns (stelliums and house emphasis)")
        return patterns

    def _analyze_complex_patterns(self, birth_chart: Dict) -> List[Dict]:
        """Analyze birth chart for complex astrological patterns.

        Args:
            birth_chart: Birth chart data

        Returns:
            List of dictionaries containing complex pattern information
        """
        self.logger.debug("Analyzing complex patterns")
        patterns = []
        aspects = birth_chart.get("aspects", [])
        planets_involved = set()

        if not aspects:
            self.logger.warning(
                "No aspects found in birth chart for complex pattern analysis.")
            return patterns

        # --- T-Square Detection ---
        self.logger.debug("Checking for T-Squares...")
        oppositions = [
            a for a in aspects if str(
                a.get("type")) in [
                "180", "opposition"]]
        squares = [
            a for a in aspects if str(
                a.get("type")) in [
                "90", "square"]]
        # Removed unused t_square_interpret variable assignment here
        found_t_squares = []

        planets_data = birth_chart.get("planets", {}) # Get planets data for sign lookup

        for opp in oppositions:
            p1 = opp["planet1"]
            p2 = opp["planet2"]

            # Find planets square to p1
            p1_squares = set()
            for sq in squares:
                if sq["planet1"] == p1:
                    p1_squares.add(sq["planet2"])
                elif sq["planet2"] == p1:
                    p1_squares.add(sq["planet1"])

            # Find planets square to p2
            p2_squares = set()
            for sq in squares:
                if sq["planet1"] == p2:
                    p2_squares.add(sq["planet2"])
                elif sq["planet2"] == p2:
                    p2_squares.add(sq["planet1"])

            # Find the common planets (apex)
            apex_planets = p1_squares.intersection(p2_squares)

            for apex in apex_planets:
                # Avoid using the same planet multiple times in different roles
                if apex == p1 or apex == p2:
                    continue

                t_square_planets = sorted([p1, p2, apex])
                t_square_key = "-".join(t_square_planets)

                if t_square_key not in found_t_squares:
                    found_t_squares.append(t_square_key)

                    # --- Enhance T-Square Interpretation ---
                    # Get signs for modality/element analysis
                    p1_sign = planets_data.get(p1, {}).get("sign")
                    p2_sign = planets_data.get(p2, {}).get("sign")
                    apex_sign = planets_data.get(apex, {}).get("sign")

                    interpretation_text = "" # Initialize interpretation text
                    if p1_sign and p2_sign and apex_sign:
                        modality = self._get_sign_modality(p1_sign) # All signs have the same modality
                        elements_present = {
                            self._get_sign_element(p1_sign),
                            self._get_sign_element(p2_sign),
                            self._get_sign_element(apex_sign)
                        }
                        all_elements = {"fire", "earth", "air", "water"}
                        missing_elements = list(all_elements - elements_present)
                        missing_element_str = missing_elements[0] if missing_elements else "None" # Should always find one

                        # Enhance interpretation with modality information
                        if modality == "cardinal":
                            modality_desc = "This Cardinal T-Square creates tension around initiating action, leadership, and taking decisive steps. The challenge involves balancing assertiveness with consideration of others."
                        elif modality == "fixed":
                            modality_desc = "This Fixed T-Square creates tension around persistence, stability, and resistance to change. The challenge involves finding flexibility while maintaining necessary structure."
                        elif modality == "mutable":
                            modality_desc = "This Mutable T-Square creates tension around adaptability, decision-making, and focused energy. The challenge involves finding consistency amid changing circumstances."

                        # Missing element description
                        missing_element_desc = f"The missing {missing_element_str.capitalize()} element suggests that integrating qualities like {self._get_element_keywords_simple(missing_element_str, modality)[0]} could help resolve this pattern's challenges." if missing_element_str != "None" else ""

                        # Fetch general description from JSON
                        pattern_info = self.structured_data.get(
                            "interpretation_patterns", {}).get(
                            "t_square", {})
                        description = pattern_info.get("description", "") # General description

                        # Combine enhanced interpretation
                        interpretation_text = (
                            f"T-Square involving {p1}, {p2}, and apex {apex}. "
                            f"{modality_desc} A T-Square forms when two planets in opposition (180 degrees apart) are both square (90 degrees) to a third planet, creating a right-angled triangle in the chart. This challenging configuration generates dynamic tension and driving energy that demands resolution through the point opposite the apex planet (known as the empty leg). The apex planet represents the focal point of the tension and often indicates an area of significant challenge and potential mastery. "
                            f"{missing_element_desc}"
                        ).strip()

                    else:
                        # Fallback to original generic interpretation if signs are missing
                        self.logger.warning(f"Could not retrieve signs for all planets in T-Square: {p1}, {p2}, {apex}. Using generic interpretation.")
                        pattern_info = self.structured_data.get(
                            "interpretation_patterns", {}).get(
                            "t_square", {})
                        description = pattern_info.get("description", "")
                        template = pattern_info.get(
                            "interpretation_template",
                            "T-Square involving {p1}, {p2}, and {apex}. {description}")
                        interpretation_text = template.format(
                            p1=p1, p2=p2, apex=apex, description=description)
                    # --- End Enhance T-Square Interpretation ---

                    patterns.append({
                        "type": "T-Square",
                        "planets": t_square_planets,
                        "opposition": sorted([p1, p2]),
                        "apex": apex,
                        "interpretation": interpretation_text # Use the enhanced or fallback text
                    })
                    planets_involved.update(
                        [p1, p2, apex])  # Track planets used

        self.logger.debug(
            f"Found {len([p for p in patterns if p['type'] == 'T-Square'])} T-Squares.")
        # --- End T-Square Detection ---

        # --- Yod Detection ---
        self.logger.debug("Checking for Yods...")
        yods = self._find_yod(aspects)
        # Removed unused yod_interpret variable assignment here

        if yods:
            for yod in yods:
                apex_planet = yod.get("apex")
                base_planets = sorted([p for p in yod.get("planets", []) if p.lower(
                ) != apex_planet.lower()])  # Ensure base planets are sorted
                all_planets = sorted(yod.get("planets", []))

                # Check if planets are already part of a larger pattern found
                # earlier
                if any(p in planets_involved for p in all_planets):
                    self.logger.debug(
                        f"Skipping Yod {all_planets} as planets are involved in another pattern.")
                    continue

                # --- Enhance Yod Interpretation ---
                apex_sign = planets_data.get(apex_planet, {}).get("sign")
                base1_sign = planets_data.get(base_planets[0], {}).get("sign")
                base2_sign = planets_data.get(base_planets[1], {}).get("sign")

                interpretation_text = "" # Initialize
                if apex_sign and base1_sign and base2_sign:
                    # Fetch general description and template from JSON
                    pattern_info = self.structured_data.get(
                        "interpretation_patterns", {}).get("yod", {})
                    description = pattern_info.get("description", "") # General description

                    # Build enhanced interpretation
                    interpretation_text = (
                        f"Yod pattern involving {base_planets[0].capitalize()} ({base1_sign}), "
                        f"{base_planets[1].capitalize()} ({base2_sign}), and apex {apex_planet.capitalize()} ({apex_sign}). "
                        f"{description} " # General Yod description
                        f"The apex planet, {apex_planet.capitalize()} in {apex_sign}, indicates the primary point of focus and necessary adjustment. "
                        f"The harmoniously linked base planets, {base_planets[0].capitalize()} in {base1_sign} and {base_planets[1].capitalize()} in {base2_sign}, "
                        f"represent skills or resources that can be utilized to navigate the pattern's challenges."
                    ).strip()
                else:
                     # Fallback to original generic interpretation if signs are missing
                    self.logger.warning(f"Could not retrieve signs for all planets in Yod: {all_planets}. Using generic interpretation.")
                    pattern_info = self.structured_data.get(
                        "interpretation_patterns", {}).get("yod", {})
                    description = pattern_info.get("description", "")
                    template = pattern_info.get(
                        "interpretation_template",
                        "Yod pattern involving {base1}, {base2}, and {apex}. {description}")  # Fallback template
                    interpretation_text = template.format(
                        base1=base_planets[0],
                        base2=base_planets[1],
                        apex=apex_planet,
                        description=description)
                # --- End Enhance Yod Interpretation ---


                patterns.append({
                    "type": "Yod",
                    "planets": all_planets,
                    "base": base_planets,
                    "apex": apex_planet,
                    "interpretation": interpretation_text # Use enhanced or fallback
                })
                planets_involved.update(all_planets)
        self.logger.debug(
            f"Found {len([p for p in patterns if p['type'] == 'Yod'])} Yods (after overlap check).")
        # --- End Yod Detection ---

        # --- Grand Trine Detection ---
        self.logger.debug("Checking for Grand Trines...")
        trines = [a for a in aspects if str(a.get("type")) in ["120", "trine"]]
        found_grand_trines = []
        planets_in_chart = list(birth_chart.get("planets", {}).keys())

        from itertools import combinations as iter_combinations
        for p1, p2, p3 in iter_combinations(planets_in_chart, 3):
            # Skip if any planet is already part of a detected pattern
            if p1 in planets_involved or p2 in planets_involved or p3 in planets_involved:
                continue

            # Check for trines between all pairs
            has_trine_12 = any((a["planet1"] == p1 and a["planet2"] == p2) or (
                a["planet1"] == p2 and a["planet2"] == p1) for a in trines)
            has_trine_13 = any((a["planet1"] == p1 and a["planet2"] == p3) or (
                a["planet1"] == p3 and a["planet2"] == p1) for a in trines)
            has_trine_23 = any((a["planet1"] == p2 and a["planet2"] == p3) or (
                a["planet1"] == p3 and a["planet2"] == p2) for a in trines)

            if has_trine_12 and has_trine_13 and has_trine_23:
                gt_planets = sorted([p1, p2, p3])
                gt_key = "-".join(gt_planets)

                if gt_key not in found_grand_trines:
                    found_grand_trines.append(gt_key)

                    pattern_info = self.structured_data.get(
                        "interpretation_patterns", {}).get("grand_trine", {})
                    description = pattern_info.get("description", "")
                    # Add a simple template here, can be refined later
                    interpretation_text = f"Grand Trine involving {p1}, {p2}, and {p3}. {description}"

                    patterns.append({
                        "type": "Grand Trine",
                        "planets": gt_planets,
                        "interpretation": interpretation_text
                    })
                    planets_involved.update(gt_planets)
                    self.logger.debug(f"Found Grand Trine: {gt_planets}")

        self.logger.debug(
            f"Found {len([p for p in patterns if p['type'] == 'Grand Trine'])} Grand Trines (after overlap check).")
        # --- End Grand Trine Detection ---

        # --- Grand Cross Detection ---
        self.logger.debug("Checking for Grand Crosses...")
        found_grand_crosses = []
        # Iterate through pairs of oppositions
        for i, opp1 in enumerate(oppositions):
            for j, opp2 in enumerate(oppositions):
                if i >= j: continue # Avoid duplicates and self-comparison

                p1 = opp1["planet1"]
                p2 = opp1["planet2"]
                p3 = opp2["planet1"]
                p4 = opp2["planet2"]

                # Check if the planets are distinct
                gc_planets_set = {p1, p2, p3, p4}
                if len(gc_planets_set) != 4:
                    continue

                # Skip if any planet is already part of a detected pattern
                if any(p in planets_involved for p in gc_planets_set):
                    continue

                # Check required squares (p1-p3, p1-p4, p2-p3, p2-p4)
                has_square_13 = any((s["planet1"] == p1 and s["planet2"] == p3) or (
                    s["planet1"] == p3 and s["planet2"] == p1) for s in squares)
                has_square_14 = any((s["planet1"] == p1 and s["planet2"] == p4) or (
                    s["planet1"] == p4 and s["planet2"] == p1) for s in squares)
                has_square_23 = any((s["planet1"] == p2 and s["planet2"] == p3) or (
                    s["planet1"] == p3 and s["planet2"] == p2) for s in squares)
                has_square_24 = any((s["planet1"] == p2 and s["planet2"] == p4) or (
                    s["planet1"] == p4 and s["planet2"] == p2) for s in squares)

                if has_square_13 and has_square_14 and has_square_23 and has_square_24:
                    gc_planets = sorted(list(gc_planets_set))
                    gc_key = "-".join(gc_planets)

                    if gc_key not in found_grand_crosses:
                        found_grand_crosses.append(gc_key)

                        pattern_info = self.structured_data.get(
    "interpretation_patterns", {}).get(
        "grand_cross", {})
                        description = pattern_info.get("description", "")
                        interpretation_text = f"Grand Cross involving {', '.join(gc_planets)}. {description}"

                        patterns.append({
                            "type": "Grand Cross",
                            "planets": gc_planets,
                            "interpretation": interpretation_text
                        })
                        planets_involved.update(gc_planets)
                        self.logger.debug(f"Found Grand Cross: {gc_planets}")

        self.logger.debug(
            f"Found {len([p for p in patterns if p['type'] == 'Grand Cross'])} Grand Crosses (after overlap check).")
        # --- End Grand Cross Detection ---

        # Add other pattern analyses here (e.g., Mystic Rectangle, Kite)

        self.logger.debug(f"Found {len(patterns)} complex patterns in total.")
        return patterns

    def _get_element_compatibility(self, element1: str, element2: str) -> str:
        """Determine compatibility category between two elements."""
        if not element1 or not element2 or element1 == "unknown" or element2 == "unknown":
            return "unknown"
        if element1 == element2:
            return "same_element"
        if (element1 in ["fire", "air"] and element2 in ["fire", "air"]) or \
           (element1 in ["earth", "water"] and element2 in ["earth", "water"]):
            return "complementary_elements"
        return "incompatible_elements"

    def _analyze_combinations(self, birth_chart: Dict) -> List[Dict]:
        """Analyze significant planetary combinations (e.g., Sun-Moon blends).

        Args:
            birth_chart: Birth chart data

        Returns:
            List of dictionaries containing combination interpretations
        """
        self.logger.debug("Analyzing planetary combinations")
        combinations = []
        # Load data for both simple sign pairings and detailed elemental combos
        simple_combinations_data = self.structured_data.get("combinations", {})
        detailed_combinations_data = self.structured_data.get(
            "interpretation_combinations", {})

        sun_moon_sign_combinations = simple_combinations_data.get(
            "sun_moon_combinations", {})
        sun_moon_element_combinations = detailed_combinations_data.get(
            "sun_moon_combinations", {})
        sun_rising_element_combinations = detailed_combinations_data.get(
            "sun_rising_combinations", {})
        moon_rising_element_combinations = detailed_combinations_data.get(
            "moon_rising_combinations", {})

        planets = birth_chart.get("planets", {})
        angles = birth_chart.get("angles", {})

        sun_sign = None
        moon_sign = None
        rising_sign = angles.get("Ascendant", {}).get("sign")

        # Get Sun/Moon signs
        if isinstance(planets, dict):
            sun_sign = planets.get("Sun", {}).get("sign")
            moon_sign = planets.get("Moon", {}).get("sign")
        elif isinstance(planets, list):
            for planet in planets:
                if planet.get("name") == "Sun":
                    sun_sign = planet.get("sign")
                elif planet.get("name") == "Moon":
                    moon_sign = planet.get("sign")

        # --- Sun-Moon Combination (Simple Sign Pairing) ---
        if sun_sign and moon_sign:
            sun_sign_lower = sun_sign.lower()
            moon_sign_lower = moon_sign.lower()

            if sun_sign_lower in sun_moon_sign_combinations and moon_sign_lower in sun_moon_sign_combinations[
                    sun_sign_lower]:
                interpretation = sun_moon_sign_combinations[sun_sign_lower][moon_sign_lower]
                combinations.append({
                    "type": "Sun-Moon Sign Pairing",
                    "planets": ["Sun", "Moon"],
                    "signs": [sun_sign, moon_sign],
                    "interpretation": interpretation
                })
                self.logger.debug(
                    f"Found Sun ({sun_sign})-Moon ({moon_sign}) sign pairing interpretation.")
            else:
                self.logger.warning(
                    f"No interpretation found for Sun ({sun_sign})-Moon ({moon_sign}) sign pairing in combinations.json.")
        else:
            self.logger.warning(
                "Sun or Moon sign missing, cannot analyze Sun-Moon sign pairing.")

        # --- Sun-Moon Combination (Elemental Theme) ---
        if sun_sign and moon_sign:
            sun_element = self._get_sign_element(sun_sign)
            moon_element = self._get_sign_element(moon_sign)
            compatibility = self._get_element_compatibility(
                sun_element, moon_element)

            if compatibility != "unknown" and compatibility in sun_moon_element_combinations:
                interpretation = sun_moon_element_combinations[compatibility].get(
                    "description", "")
                combinations.append({
                    "type": "Sun-Moon Elemental Theme",
                    "planets": ["Sun", "Moon"],
                    "elements": [sun_element, moon_element],
                    "compatibility": compatibility,
                    "interpretation": interpretation
                })
                self.logger.debug(
                    f"Found Sun ({sun_element})-Moon ({moon_element}) elemental theme ({compatibility}).")
            else:
                self.logger.warning(
                    f"Could not determine Sun-Moon elemental theme for {sun_element}-{moon_element}.")

        # --- Sun-Rising Combination (Elemental Theme) ---
        if sun_sign and rising_sign:
            sun_element = self._get_sign_element(sun_sign)
            rising_element = self._get_sign_element(rising_sign)
            compatibility = self._get_element_compatibility(
                sun_element, rising_element)

            if compatibility != "unknown" and compatibility in sun_rising_element_combinations:
                interpretation = sun_rising_element_combinations[compatibility].get(
                    "description", "")
                combinations.append({
                    "type": "Sun-Rising Elemental Theme",
                    "points": ["Sun", "Ascendant"],
                    "elements": [sun_element, rising_element],
                    "compatibility": compatibility,
                    "interpretation": interpretation
                })
                self.logger.debug(
                    f"Found Sun ({sun_element})-Rising ({rising_element}) elemental theme ({compatibility}).")
            else:
                self.logger.warning(
                    f"Could not determine Sun-Rising elemental theme for {sun_element}-{rising_element}.")
        else:
            self.logger.warning(
                "Sun or Rising sign missing, cannot analyze Sun-Rising elemental theme.")

        # --- Moon-Rising Combination (Elemental Theme) ---
        if moon_sign and rising_sign:
            moon_element = self._get_sign_element(moon_sign)
            rising_element = self._get_sign_element(rising_sign)
            compatibility = self._get_element_compatibility(
                moon_element, rising_element)

            if compatibility != "unknown" and compatibility in moon_rising_element_combinations:
                interpretation = moon_rising_element_combinations[compatibility].get(
                    "description", "")
                combinations.append({
                    "type": "Moon-Rising Elemental Theme",
                    "points": ["Moon", "Ascendant"],
                    "elements": [moon_element, rising_element],
                    "compatibility": compatibility,
                    "interpretation": interpretation
                })
                self.logger.debug(
                    f"Found Moon ({moon_element})-Rising ({rising_element}) elemental theme ({compatibility}).")
            else:
                self.logger.warning(
                    f"Could not determine Moon-Rising elemental theme for {moon_element}-{rising_element}.")
        else:
            self.logger.warning(
                "Moon or Rising sign missing, cannot analyze Moon-Rising elemental theme.")

        self.logger.debug(
            f"Found {len(combinations)} planetary combinations in total")
        return combinations

    # --- New Method for Chart Shape Analysis (Placeholder) ---
    def _analyze_chart_shape(self, birth_chart: Dict) -> Dict:
        """Analyze the chart shape based on planetary distribution. (Placeholder)

        Args:
            birth_chart: Birth chart data

        Returns:
            Dictionary containing chart shape information
        """
        # TODO: Implement full chart shape calculation logic
        # self.logger.info("Chart shape analysis not fully implemented yet.") # Remove placeholder log
        shape_data = self.structured_data.get("chart_shapes", {})
        definitions = shape_data.get("definitions", {})
        interpretations = shape_data.get("interpretations", {})

        if not definitions or not interpretations:
            self.logger.warning("Chart shape definitions or interpretations not found in structured data.")
            return {"shape_name": "Undetermined", "interpretation": "Chart shape data unavailable."}

        planets_to_use = definitions.get("planets_to_use", [])
        planets_in_chart = birth_chart.get("planets", {})

        degrees = [] # List to hold planet degrees
        for planet_name in planets_to_use:
            planet_data = None
            if isinstance(planets_in_chart, dict) and planet_name in planets_in_chart:
                planet_data = planets_in_chart[planet_name]
            elif isinstance(planets_in_chart, list):
                for p in planets_in_chart:
                    if p.get('name') == planet_name:
                        planet_data = p
                        break
            
            if planet_data:
                degree = planet_data.get('degree')
                if degree is not None:
                    degrees.append(degree)
                else:
                     self.logger.warning(f"Degree not found for planet {planet_name} in chart shape analysis.")

        if len(degrees) < 3: # Need at least 3 planets for meaningful shape
            self.logger.info(f"Not enough planets ({len(degrees)}) for chart shape analysis.")
            return {"shape_name": "Undetermined", "occupied_span_degrees": None, "largest_gap_degrees": None, "interpretation": interpretations.get("undetermined", "Chart shape could not be determined.")}

        # Sort degrees
        degrees.sort()

        # Calculate gaps (including wrap-around)
        gaps = []
        for i in range(len(degrees) - 1):
            gap = degrees[i+1] - degrees[i]
            gaps.append(gap)
        # Add wrap-around gap
        wrap_gap = (360.0 - degrees[-1]) + degrees[0]
        gaps.append(wrap_gap)

        if not gaps: # Should not happen if len(degrees) >= 3
             self.logger.error("Could not calculate gaps for chart shape analysis.")
             return {"shape_name": "Error", "occupied_span_degrees": None, "largest_gap_degrees": None, "interpretation": "Error calculating gaps."}

        largest_gap = max(gaps)
        occupied_span = 360.0 - largest_gap

        # Determine shape based on definitions
        shape_name = "undetermined" # Default

        # Load definitions for comparison
        bundle_def = definitions.get("bundle", {})
        bowl_def = definitions.get("bowl", {})
        locomotive_def = definitions.get("locomotive", {})
        splash_def = definitions.get("splash", {})
        # Note: Seesaw and Splay require cluster analysis, not implemented here

        # Check shapes in order of potential overlap (most restrictive first)
        if occupied_span <= bundle_def.get("max_span_degrees", 120):
            shape_name = "bundle"
        elif occupied_span <= bowl_def.get("max_span_degrees", 180) and largest_gap >= bowl_def.get("min_gap_degrees", 180):
             # Make sure the gap is actually the defining feature, not just a small span
             if largest_gap > occupied_span: # Ensure gap is larger than span for a true bowl
                shape_name = "bowl"
        elif largest_gap >= locomotive_def.get("min_gap_degrees", 120) and largest_gap <= locomotive_def.get("max_gap_degrees", 240):
            # Check locomotive *after* bowl/bundle as it can overlap
             shape_name = "locomotive"
        elif largest_gap <= splash_def.get("max_gap_degrees", 90):
             # Basic Splash Check (more conditions like occupied signs could be added)
             shape_name = "splash"
        # More checks can be added here

        # Get interpretation
        interpretation = interpretations.get(shape_name, interpretations.get("undetermined", "")) # Use determined shape_name

        self.logger.debug(f"Determined chart shape: {shape_name} (Span: {occupied_span:.1f}, Gap: {largest_gap:.1f})")
        self.logger.debug(f"Shape interpretation type: {type(interpretation).__name__}, value: {interpretation}")

        return {
            "shape_name": shape_name.capitalize(),
            "occupied_span_degrees": round(occupied_span, 1),
            "largest_gap_degrees": round(largest_gap, 1),
            "interpretation": interpretation
        }
    # --- End Chart Shape Analysis Method ---
