"""Astrological interpretation service module."""

# Standard library imports
from datetime import datetime
import json
import logging
import os
from typing import Dict, Any, List, Tuple, Union

# Third-party imports
from flatlib.datetime import Datetime

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
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
        
        self.logger.info("Initializing InterpretationService")
        
        # Set project root for file paths
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logger.debug(f"Project root: {self.project_root}")
        
        # Initialize data structures
        self.structured_data = {}
        self.birth_chart = None
        
        # Initialize caches
        self._aspect_cache = {}
        self._planet_cache = {}
        self._house_cache = {}
        self._sign_cache = {}
        
        # Load structured data
        self._load_all_structured_data()
        
        # Initialize caches after loading data
        self._initialize_caches()
        
        self.logger.info("InterpretationService initialized successfully")
        
    def _load_all_structured_data(self):
        """Load all structured data from JSON files."""
        self.logger.info("Loading all structured data files")
        structured_data_dir = os.path.join(self.project_root, "data", "structured")
        
        try:
            # Get all JSON files in the structured data directory
            if not os.path.exists(structured_data_dir):
                self.logger.error(f"Structured data directory not found: {structured_data_dir}")
                return
                
            json_files = [f.replace('.json', '') for f in os.listdir(structured_data_dir) 
                          if f.endswith('.json')]
            self.logger.debug(f"Found {len(json_files)} JSON files: {json_files}")
            
            # Load each file
            for file_name in json_files:
                self.structured_data[file_name] = self._load_structured_data(file_name)
                
            # Log loaded data sources
            self.logger.info(f"Loaded structured data sources: {list(self.structured_data.keys())}")
            
            # Convert numeric aspect types to strings for consistency
            if "aspects" in self.structured_data:
                aspect_data = self.structured_data["aspects"]
                aspect_types_to_add = {}
                
                for key, data in list(aspect_data.items()):
                    if "angle" in data:
                        angle_str = str(data["angle"])
                        self.logger.debug(f"Converting aspect type {key} to numeric key {angle_str}")
                        aspect_types_to_add[angle_str] = data
            
            # Add the new aspect types separately
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
            self.logger.error(f"Error loading all structured data: {str(e)}", exc_info=True)

    def _load_structured_data(self, file_name: str) -> Dict:
        """Load structured data from JSON files.
        
        Args:
            file_name: Name of the JSON file to load
            
        Returns:
            Dictionary containing the structured data
        """
        self.logger.debug(f"Loading structured data file: {file_name}")
        structured_data_dir = os.path.join(self.project_root, "data", "structured")
        file_path = os.path.join(structured_data_dir, f"{file_name}.json")
        
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"Structured data file not found: {file_path}")
                return {}
                
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.debug(f"Successfully loaded {file_name}.json with {len(data)} top-level keys")
                
                # Log the top-level keys to understand structure
                if isinstance(data, dict):
                    self.logger.debug(f"Top-level keys in {file_name}.json: {list(data.keys())}")
                elif isinstance(data, list):
                    self.logger.debug(f"Loaded list data from {file_name}.json with {len(data)} items")
                    
                return data
        except json.JSONDecodeError:
            self.logger.error(f"Error parsing JSON from {file_path}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading structured data from {file_path}: {str(e)}")
            return {}

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
                    self.logger.error(f"Planet {planet_name} data must be a dictionary")
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

    def generate_interpretation(self, birth_chart: Dict, level: str = "basic") -> Dict:
        """Generate an interpretation based on the birth chart.
        
        Args:
            birth_chart: Birth chart data
            level: Interpretation detail level ('basic', 'intermediate', 'detailed')
            
        Returns:
            Dictionary containing interpretation data
        """
        self.logger.info(f"Generating {level} interpretation for birth chart")
        
        # Validate birth chart
        if not self._validate_birth_chart(birth_chart):
            self.logger.error("Invalid birth chart provided")
            return {"status": "error", "message": "Invalid birth chart data"}
                
        # Store birth chart for use in methods
        self.birth_chart = birth_chart
        
        # Log birth chart details
        self.logger.debug(f"Birth chart has {len(birth_chart.get('planets', {}))} planets and " 
                         f"{len(birth_chart.get('houses', {}))} houses")
        self.logger.debug(f"Planets in chart: {list(birth_chart.get('planets', {}).keys())}")
        
        # Create interpretation object
        interpretation = {
            "status": "success",
            "birth_chart": birth_chart,
                "planets": [],
                "houses": [],
                "aspects": [],
                "patterns": [],
            "element_balance": {},
            "modality_balance": {},
            "overall": "",
        }
        
        # Add planet interpretations
        self.logger.debug("Generating planet interpretations")
        planet_interpretations = self._generate_planet_interpretations(birth_chart, level)
        interpretation["planets"] = planet_interpretations
        self.logger.debug(f"Generated interpretations for {len(planet_interpretations)} planets")
        
        # Add house interpretations
        self.logger.debug("Generating house interpretations")
        house_interpretations = self._generate_house_interpretations(birth_chart, level)
        interpretation["houses"] = house_interpretations
        self.logger.debug(f"Generated interpretations for {len(house_interpretations)} houses")
        
        # Add aspect interpretations
        self.logger.debug("Generating aspect interpretations")
        aspect_interpretations = self._generate_aspect_interpretations(birth_chart, level)
        interpretation["aspects"] = aspect_interpretations
        self.logger.debug(f"Generated interpretations for {len(aspect_interpretations)} aspects")
        
        # Add element and modality balance
        self.logger.debug("Analyzing element balance")
        element_balance = self._analyze_simple_element_balance(birth_chart)
        interpretation["element_balance"] = element_balance
        self.logger.debug(f"Element balance: {element_balance}")
        
        self.logger.debug("Analyzing modality balance")
        modality_balance = self._analyze_simple_modality_balance(birth_chart)
        interpretation["modality_balance"] = modality_balance
        self.logger.debug(f"Modality balance: {modality_balance}")
        
        # Add simple patterns (like stelliums, element emphasis)
        self.logger.debug("Analyzing simple patterns")
        simple_patterns = self._analyze_simple_patterns(birth_chart)
        interpretation["simple_patterns"] = simple_patterns
        self.logger.debug(f"Found {len(simple_patterns)} simple patterns")
        
        # Get pattern interpretations (complex)
        self.logger.debug("Analyzing complex patterns")
        pattern_interpretations = self._analyze_complex_patterns(self.birth_chart)
        interpretation["patterns"] = pattern_interpretations
        self.logger.debug(f"Analyzed {len(pattern_interpretations)} complex patterns")
        
        # Add planetary combinations analysis
        self.logger.debug("Analyzing planetary combinations")
        combinations = self._analyze_combinations(birth_chart)
        interpretation["combinations"] = combinations
        self.logger.debug(f"Found {len(combinations)} significant planetary combinations")
        
        # Generate overall interpretation
        self.logger.debug("Generating overall interpretation")
        overall = self._generate_overall_interpretation(birth_chart, level)
        interpretation["overall"] = overall
        self.logger.debug("Overall interpretation generated")
        
        # Include rising sign summary if ascendant is available
        ascendant = birth_chart.get("angles", {}).get("Ascendant", {}).get("sign")
        if ascendant:
            self.logger.debug(f"Generating rising sign summary for {ascendant}")
            rising_summary = self._get_rising_sign_summary(ascendant)
            interpretation["rising_summary"] = rising_summary
            self.logger.debug("Rising sign summary generated")
        
        self.logger.info("Interpretation generation completed successfully")
        return interpretation

    def _generate_planet_interpretations(self, birth_chart: Dict, level: str = "basic") -> List[Dict]:
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
                interpretation = self._get_planet_interpretation(planet_name, sign, house, retrograde)
                
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
                interpretation = self._get_planet_interpretation(name, sign, house, retrograde)
                
                planet_interpretations.append({
                    "planet": name,
                    "sign": sign,
                    "house": house,
                    "retrograde": retrograde,
                    "interpretation": interpretation
                })
                
        self.logger.debug(f"Generated {len(planet_interpretations)} planet interpretations")
        return planet_interpretations
        
    def _get_planet_interpretation(self, planet: str, sign: str, house: int, retrograde: bool = False) -> str:
        """Generate interpretation for a planet in a sign and house.
        
        Args:
            planet: Planet name
            sign: Zodiac sign
            house: House number
            retrograde: Whether the planet is retrograde
            
        Returns:
            Interpretation text
        """
        self.logger.debug(f"Generating interpretation for {planet} in {sign} (House {house})")
        
        # Normalize inputs
        planet_lower = planet.lower()
        sign_lower = sign.lower()
        house_str = str(house)
        
        # Attempt to get richer descriptions from structured data
        planet_data = self.structured_data.get("planets", {}).get(planet_lower, {})
        sign_data = self.structured_data.get("signs", {}).get(sign_lower, {})
        house_data = self.structured_data.get("houses", {}).get(house_str, {})
        
        # Extract descriptions or use fallbacks
        planet_desc = planet_data.get("description", f"The {planet.capitalize()} represents its core energies.")
        sign_desc_intro = f"In the sign of {sign.capitalize()}, these energies are expressed through qualities like {sign_data.get('keywords', [sign_lower])[0]} and {sign_data.get('keywords', [sign_lower])[1]}."
        sign_detail = sign_data.get("description", f"{sign.capitalize()} brings its characteristic traits.")
        house_meaning = house_data.get("meaning", f"the area of life associated with House {house}")
        house_desc = f"Placed in House {house}, this influence manifests particularly in relation to {house_meaning}."

        # Build the interpretation using structured data if available
        interpretation_parts = [
            f"{planet.capitalize()} in {sign.capitalize()} (House {house}):",
            planet_desc, 
            sign_desc_intro,
            # Include a snippet of the sign's detailed description for context
            f"Specifically, {sign.capitalize()} influence here suggests {sign_detail.split('.')[0]}.", 
            house_desc
        ]
        
        interpretation = " ".join(interpretation_parts)
        
        # Add retrograde interpretation if applicable
        if retrograde:
            interpretation += f" With {planet.capitalize()} retrograde, these energies are often internalized, prompting deeper reflection or unconventional expression." 
            
        # Add dignity interpretation
        dignity = self._get_essential_dignity(planet_lower, sign_lower)
        dignity_text = {
            "rulership": f"{planet.capitalize()} is strongly placed in its rulership sign, {sign.capitalize()}, allowing its energies to flow powerfully and naturally.",
            "exaltation": f"{planet.capitalize()} is exalted in {sign.capitalize()}, suggesting its highest potential can be expressed here.",
            "detriment": f"{planet.capitalize()} is in detriment in {sign.capitalize()}, indicating potential challenges or the need for conscious effort in expressing its energy.",
            "fall": f"{planet.capitalize()} is in its fall in {sign.capitalize()}, suggesting that expressing its energy may require significant awareness and development."
        }
        if dignity in dignity_text:
             interpretation += f" {dignity_text[dignity]}"
             
        return interpretation
        
    def _generate_house_interpretations(self, birth_chart: Dict, level: str = "basic") -> List[Dict]:
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
                    interpretation = self._get_house_interpretation(house_num, sign)
                    
                    house_interpretations.append({
                        "house": house_num,
                        "sign": sign,
                        "interpretation": interpretation
                    })
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid house number: {house_num_str}")
                    continue
        elif isinstance(houses_data, list):
            # List format (old)
            for house in houses_data:
                house_num = house.get("house_num")
                sign = house.get("sign")
                
                if house_num is None or not sign:
                    continue
                    
                # Generate interpretation
                interpretation = self._get_house_interpretation(house_num, sign)
                
                house_interpretations.append({
                    "house": house_num,
                    "sign": sign,
                    "interpretation": interpretation
                })
                
        self.logger.debug(f"Generated {len(house_interpretations)} house interpretations")
        return house_interpretations
        
    def _get_house_interpretation(self, house_num: int, sign: str) -> str:
        """Generate interpretation for a house with a specific sign on its cusp.
        
        Args:
            house_num: House number
            sign: Zodiac sign on the house cusp
            
        Returns:
            Interpretation text
        """
        self.logger.debug(f"Generating interpretation for House {house_num} with {sign} on cusp")
        
        # Normalize inputs
        sign_lower = sign.lower()
        house_str = str(house_num)
        
        # Get house meanings
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

        # Get sign qualities
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

        house_meaning = house_meanings.get(house_str, f"house {house_num} matters")
        sign_quality = sign_qualities.get(sign_lower, sign_lower)
        
        # Build interpretation
        interpretation = f"House {house_num} with {sign.capitalize()} on the cusp influences {house_meaning}. "
        interpretation += f"This brings {sign_quality} qualities to this area of life. "
        
        return interpretation
        
    def _generate_aspect_interpretations(self, birth_chart: Dict, level: str = "basic") -> List[Dict]:
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
            interpretation = self._get_aspect_interpretation(planet1, planet2, aspect_type, orb)
            
            if interpretation:
                aspect_interpretations.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "type": aspect_type,
                    "orb": orb,
                    "interpretation": interpretation
                })
                
        self.logger.debug(f"Generated {len(aspect_interpretations)} aspect interpretations")
        return aspect_interpretations
        
    def _get_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: Union[int, str], orb: float = 0) -> str:
        """Generate interpretation for an aspect between two planets.
        
        Args:
            planet1: First planet
            planet2: Second planet
            aspect_type: Type of aspect (0/conjunction, 60/sextile, 90/square, 120/trine, 180/opposition)
            orb: Orb of the aspect
            
        Returns:
            Interpretation text
        """
        self.logger.debug(f"Generating interpretation for {planet1}-{planet2} {aspect_type} aspect")
        
        # Normalize planets
        planet1_lower = planet1.lower()
        planet2_lower = planet2.lower()
        
        # Get aspect name and quality
        aspect_names = {
            0: "conjunction",
            "0": "conjunction",
            "conjunction": "conjunction",
            60: "sextile",
            "60": "sextile",
            "sextile": "sextile",
            90: "square",
            "90": "square",
            "square": "square",
            120: "trine",
            "120": "trine",
            "trine": "trine",
            180: "opposition",
            "180": "opposition",
            "opposition": "opposition"
        }
        
        aspect_qualities = {
            "conjunction": "combines and intensifies",
            "sextile": "harmonizes and creates opportunities between",
            "square": "creates tension and challenges between",
            "trine": "harmonizes and facilitates flow between",
            "opposition": "creates polarization and awareness between"
        }
        
        # Get planet keywords
        planet_keywords = {
            "sun": "identity and conscious self",
            "moon": "emotions and instincts",
            "mercury": "communication and thinking",
            "venus": "relationships and values",
            "mars": "action and drive",
            "jupiter": "expansion and growth",
            "saturn": "structure and limitations",
            "uranus": "innovation and rebellion",
            "neptune": "dreams and spirituality",
            "pluto": "transformation and power",
            "north_node": "life direction",
            "south_node": "past patterns"
        }
        
        # Convert aspect type to string for lookup
        aspect_str = str(aspect_type)
        aspect_name = aspect_names.get(aspect_type, None)
        
        if not aspect_name or aspect_name == "-1":
            return None
            
        aspect_quality = aspect_qualities.get(aspect_name, "influences")
        planet1_keyword = planet_keywords.get(planet1_lower, planet1)
        planet2_keyword = planet_keywords.get(planet2_lower, planet2)
        
        # Build interpretation
        interpretation = f"{planet1.capitalize()} {aspect_name} {planet2.capitalize()}: This aspect {aspect_quality} {planet1_keyword} and {planet2_keyword}. "
        
        # Add orb significance
        if orb < 2:
            interpretation += "This aspect is very strong with a tight orb, making its influence particularly significant. "
        elif orb > 8:
            interpretation += "This aspect has a wide orb, so its influence may be more subtle. "
            
        return interpretation
        
    def _generate_overall_interpretation(self, birth_chart: Dict, level: str = "basic") -> str:
        """Generate an overall interpretation of the birth chart.
        
        Args:
            birth_chart: Birth chart data
            level: Level of detail for the interpretation
            
        Returns:
            Overall interpretation text
        """
        self.logger.debug(f"Generating {level} overall interpretation")
        
        # Get element and modality balances
        element_balance = self._analyze_simple_element_balance(birth_chart)
        modality_balance = self._analyze_simple_modality_balance(birth_chart)
        
        # Generate interpretation
        interpretation_parts = []
        
        # Add element balance interpretation
        if element_balance and "interpretation" in element_balance:
            interpretation_parts.append(element_balance["interpretation"])
            
        # Add modality balance interpretation
        if modality_balance and "interpretation" in modality_balance:
            interpretation_parts.append(modality_balance["interpretation"])
            
        # Add aspect balance
        aspects = birth_chart.get("aspects", [])
        harmonious_count = 0
        challenging_count = 0
        
        for aspect in aspects:
            aspect_type = aspect.get("type")
            if aspect_type in [60, "60", "sextile", 120, "120", "trine"]:
                harmonious_count += 1
            elif aspect_type in [90, "90", "square", 180, "180", "opposition"]:
                challenging_count += 1
                
        if harmonious_count > challenging_count * 1.5:
            interpretation_parts.append(
                "Your chart shows a predominance of harmonious aspects, suggesting natural flow and ease in many areas of life."
            )
        elif challenging_count > harmonious_count * 1.5:
            interpretation_parts.append(
                "Your chart features more challenging aspects, indicating opportunities for growth through overcoming obstacles."
            )
        else:
            interpretation_parts.append(
                "Your chart shows a balanced mix of harmonious and challenging aspects, suggesting a well-rounded life experience."
            )
            
        # Add summary sentence
        interpretation_parts.append(
            "This natal chart represents a unique combination of energies and potential that unfolds throughout your life."
        )
        
        # Combine all parts
        interpretation = " ".join(interpretation_parts)
        
        self.logger.debug(f"Generated overall interpretation: {interpretation[:50]}...")
        return interpretation

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
            self.logger.warning(f"Unknown sign for element determination: {sign}")
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
            self.logger.warning(f"Unknown sign for modality determination: {sign}")
            return "unknown"

    def _get_rising_sign_summary(self, rising_sign: str) -> str:
        """Generate a summary based on the rising sign (Ascendant).
        
        Args:
            rising_sign: The rising sign
            
        Returns:
            Summary text
        """
        self.logger.debug(f"Generating rising sign summary for: {rising_sign}")
        
        # First, try to get a summary from structured data
        rising_sign_data = self.structured_data.get("descriptions", {}).get("rising_signs", {})
        rising_sign_lower = rising_sign.lower()
        
        if rising_sign_lower in rising_sign_data:
            self.logger.debug(f"Found rising sign summary in structured data for {rising_sign}")
            return rising_sign_data[rising_sign_lower]
        
        # If no structured data, use default descriptions
        self.logger.debug(f"No structured data for rising sign {rising_sign}, using default description")
        rising_signs = {
            "aries": (
                "With Aries rising, you approach life with dynamism and assertiveness. "
                "You make a strong first impression with your direct, straightforward manner. "
                "Your physical appearance may feature distinctive facial features, a athletic build, "
                "and expressive eyes. Your demeanor is typically confident, enthusiastic, and action-oriented. "
                "You tend to be perceived as brave, independent, and occasionally impulsive."
            ),
            "taurus": (
                "With Taurus rising, you approach life with stability and dependability. "
                "You make a solid first impression with your grounded, practical manner. "
                "Your physical appearance may feature a strong build, expressive eyes, and a sensual quality. "
                "Your demeanor is typically patient, reliable, and appreciative of beauty and comfort. "
                "You tend to be perceived as steady, determined, and occasionally stubborn."
            ),
            "gemini": (
                "With Gemini rising, you approach life with curiosity and adaptability. "
                "You make an engaging first impression with your communicative, versatile manner. "
                "Your physical appearance may feature expressive hands, a youthful quality, and quick movements. "
                "Your demeanor is typically animated, inquisitive, and mentally active. "
                "You tend to be perceived as clever, sociable, and occasionally scattered."
            ),
            "cancer": (
                "With Cancer rising, you approach life with sensitivity and nurturing instincts. "
                "You make a caring first impression with your receptive, protective manner. "
                "Your physical appearance may feature a round face, pale complexion, and a gentle quality. "
                "Your demeanor is typically empathetic, intuitive, and emotionally responsive. "
                "You tend to be perceived as supportive, cautious, and occasionally moody."
            ),
            "leo": (
                "With Leo rising, you approach life with warmth and confidence. "
                "You make a charismatic first impression with your dignified, expressive manner. "
                "Your physical appearance may feature a mane-like hairstyle, a noble bearing, and a radiant smile. "
                "Your demeanor is typically dramatic, generous, and naturally commanding. "
                "You tend to be perceived as creative, proud, and occasionally domineering."
            ),
            "virgo": (
                "With Virgo rising, you approach life with analysis and practicality. "
                "You make a precise first impression with your detailed, helpful manner. "
                "Your physical appearance may feature clean lines, a neat presentation, and an alert expression. "
                "Your demeanor is typically organized, discriminating, and methodical. "
                "You tend to be perceived as intelligent, health-conscious, and occasionally critical."
            ),
            "libra": (
                "With Libra rising, you approach life with harmony and diplomacy. "
                "You make a graceful first impression with your balanced, cooperative manner. "
                "Your physical appearance may feature symmetrical features, a refined style, and a pleasant smile. "
                "Your demeanor is typically fair-minded, artistic, and socially adept. "
                "You tend to be perceived as charming, peace-loving, and occasionally indecisive."
            ),
            "scorpio": (
                "With Scorpio rising, you approach life with intensity and depth. "
                "You make a powerful first impression with your magnetic, mysterious manner. "
                "Your physical appearance may feature penetrating eyes, a focused gaze, and a compelling presence. "
                "Your demeanor is typically perceptive, passionate, and strategically reserved. "
                "You tend to be perceived as profound, resourceful, and occasionally intimidating."
            ),
            "sagittarius": (
                "With Sagittarius rising, you approach life with optimism and exploration. "
                "You make an expansive first impression with your enthusiastic, philosophical manner. "
                "Your physical appearance may feature a tall stature, an open expression, and athletic qualities. "
                "Your demeanor is typically honest, adventurous, and freedom-loving. "
                "You tend to be perceived as jovial, open-minded, and occasionally tactless."
            ),
            "capricorn": (
                "With Capricorn rising, you approach life with discipline and purpose. "
                "You make a responsible first impression with your serious, ambitious manner. "
                "Your physical appearance may feature a dignified bearing, pronounced bone structure, and a reserved quality. "
                "Your demeanor is typically mature, cautious, and goal-oriented. "
                "You tend to be perceived as reliable, authoritative, and occasionally austere."
            ),
            "aquarius": (
                "With Aquarius rising, you approach life with originality and objectivity. "
                "You make a distinctive first impression with your independent, progressive manner. "
                "Your physical appearance may feature unique style choices, electric energy, and a friendly yet detached quality. "
                "Your demeanor is typically innovative, humanitarian, and intellectually curious. "
                "You tend to be perceived as unconventional, equality-minded, and occasionally aloof."
            ),
            "pisces": (
                "With Pisces rising, you approach life with receptivity and compassion. "
                "You make a gentle first impression with your empathetic, dreamy manner. "
                "Your physical appearance may feature soft features, luminous eyes, and a fluid quality of movement. "
                "Your demeanor is typically intuitive, artistic, and emotionally attuned. "
                "You tend to be perceived as imaginative, spiritual, and occasionally evasive."
            ),
        }
        
        description = rising_signs.get(rising_sign_lower, 
            f"Your {rising_sign} Ascendant colors how others perceive you initially and shapes your approach to new situations."
        )
        
        self.logger.debug(f"Used default rising sign description for {rising_sign}")
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
        
        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC
                if planet_name.lower() in ["ascendant", "midheaven", "descendant", "ic"]:
                    continue
                    
                sign = planet_data.get("sign", "").lower()
                element = self._get_sign_element(sign)
                
                if element in elements:
                    elements[element] += 1
                    element_planets[element].append(planet_name)
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC
                if planet.get("name", "").lower() in ["ascendant", "midheaven", "descendant", "ic"]:
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
        sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_elements[0][0] if sorted_elements[0][1] > 0 else None
        lacking = [element for element, count in elements.items() if count <= 1]
        
        # Generate interpretation
        interpretation = self._generate_element_balance_interpretation(dominant, lacking, percentages)
        
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
        
    def _generate_element_balance_interpretation(self, dominant: str, lacking: List[str], percentages: Dict[str, float]) -> str:
        """Generate an interpretation of the element balance.
        
        Args:
            dominant: Dominant element
            lacking: List of lacking elements
            percentages: Element percentages
            
        Returns:
            Interpretation text
        """
        element_descriptions = {
            "fire": "passion, creativity, and assertiveness",
            "earth": "practicality, stability, and material focus",
            "air": "mental activity, communication, and social connection",
            "water": "emotional depth, intuition, and sensitivity"
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
        
        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC
                if planet_name.lower() in ["ascendant", "midheaven", "descendant", "ic"]:
                    continue
                    
                sign = planet_data.get("sign", "").lower()
                modality = self._get_sign_modality(sign)
                
                if modality in modalities:
                    modalities[modality] += 1
                    modality_planets[modality].append(planet_name)
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC
                if planet.get("name", "").lower() in ["ascendant", "midheaven", "descendant", "ic"]:
                    continue
                    
                sign = planet.get("sign", "").lower()
                modality = self._get_sign_modality(sign)
                
                if modality in modalities:
                    modalities[modality] += 1
                    modality_planets[modality].append(planet.get("name"))

        # Calculate percentages
        total_planets = sum(modalities.values())
        percentages = {}

        if total_planets > 0:
            for modality, count in modalities.items():
                percentages[modality] = round((count / total_planets) * 100, 2)
        
        # Determine dominant and lacking modalities
        dominant = None
        if total_planets > 0:
             sorted_modalities = sorted(modalities.items(), key=lambda x: x[1], reverse=True)
             if sorted_modalities and sorted_modalities[0][1] > 0: # Added check if sorted_modalities is not empty
                 dominant = sorted_modalities[0][0]
        lacking = [modality for modality, count in modalities.items() if count <= 1]
        
        # Generate interpretation
        interpretation = self._generate_modality_balance_interpretation(dominant, lacking, percentages)
        
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
        
    def _generate_modality_balance_interpretation(self, dominant: str, lacking: List[str], percentages: Dict[str, float]) -> str:
        """Generate an interpretation of the modality balance.
        
        Args:
            dominant: Dominant modality
            lacking: List of lacking modalities
            percentages: Modality percentages
            
        Returns:
            Interpretation text
        """
        modality_descriptions = {
            "cardinal": "initiating action, leadership, and pioneering",
            "fixed": "persistence, stability, and determination",
            "mutable": "adaptability, flexibility, and versatility"
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
        
        # Process planets (handling both dictionary and list formats)
        planets_data = birth_chart.get("planets", {})
        
        if isinstance(planets_data, dict):
            # Dictionary format (new)
            for planet_name, planet_data in planets_data.items():
                # Skip points like Ascendant, MC
                if planet_name.lower() in ["ascendant", "midheaven", "descendant", "ic"]:
                    continue
                
                sign = planet_data.get("sign")
                if sign:
                    sign_lower = sign.lower()
                    sign_counts[sign_lower] = sign_counts.get(sign_lower, 0) + 1
                    
                    if sign_lower not in sign_planets:
                        sign_planets[sign_lower] = []
                    sign_planets[sign_lower].append(planet_name)
        elif isinstance(planets_data, list):
            # List format (old)
            for planet in planets_data:
                # Skip points like Ascendant, MC
                if planet.get("name", "").lower() in ["ascendant", "midheaven", "descendant", "ic"]:
                    continue
                    
                sign = planet.get("sign")
                if sign:
                    sign_lower = sign.lower()
                    sign_counts[sign_lower] = sign_counts.get(sign_lower, 0) + 1
                    
                    if sign_lower not in sign_planets:
                        sign_planets[sign_lower] = []
                    sign_planets[sign_lower].append(planet.get("name"))
                    
        # Find stelliums
        for sign, count in sign_counts.items():
            if count >= 3:  # Consider 3+ planets a stellium
                    patterns.append({
                        "type": "stellium",
                        "sign": sign,
                    "planets": sign_planets[sign],
                    "count": count,
                    "interpretation": f"You have a stellium in {sign.capitalize()} with {count} planets ({', '.join(sign_planets[sign])}). This concentration amplifies {sign.capitalize()} qualities in your chart."
                })
                
        self.logger.debug(f"Found {len(patterns)} simple patterns")
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
            self.logger.warning("No aspects found in birth chart for complex pattern analysis.")
            return patterns

        # --- T-Square Detection --- 
        self.logger.debug("Checking for T-Squares...")
        oppositions = [a for a in aspects if str(a.get("type")) in ["180", "opposition"]]
        squares = [a for a in aspects if str(a.get("type")) in ["90", "square"]]
        t_square_interpret = self.structured_data.get("interpretation_patterns", {}).get("t_square", {}).get("description", "")
        found_t_squares = []

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
                    interpretation_text = (
                        f"T-Square involving {p1} opposite {p2}, both square {apex}. "
                        f"The apex planet {apex} is a focal point of tension and drive. "
                        f"{t_square_interpret}"
                    )
                    patterns.append({
                        "type": "T-Square",
                        "planets": t_square_planets,
                        "opposition": sorted([p1, p2]),
                        "apex": apex,
                        "interpretation": interpretation_text
                    })
                    planets_involved.update([p1, p2, apex]) # Track planets used

        self.logger.debug(f"Found {len([p for p in patterns if p['type'] == 'T-Square'])} T-Squares.")
        # --- End T-Square Detection ---
            
        # --- Yod Detection --- 
        self.logger.debug("Checking for Yods...")
        yods = self._find_yod(aspects)
        yod_interpret = self.structured_data.get("interpretation_patterns", {}).get("yod", {}).get("description", "")
        if yods:
            for yod in yods:
                apex_planet = yod.get("apex")
                base_planets = sorted([p for p in yod.get("planets", []) if p.lower() != apex_planet.lower()]) # Ensure base planets are sorted
                all_planets = sorted(yod.get("planets", []))
                
                # Check if planets are already part of a larger pattern found earlier
                if any(p in planets_involved for p in all_planets):
                     self.logger.debug(f"Skipping Yod {all_planets} as planets are involved in another pattern.")
                     continue
                     
                interpretation_text = (
                    f"Yod pattern involving {base_planets[0]} and {base_planets[1]} pointing to {apex_planet}. "
                    f"This indicates a point of adjustment or special focus. "
                    f"{yod_interpret}"
                )
                patterns.append({
                    "type": "Yod",
                    "planets": all_planets,
                    "base": base_planets,
                    "apex": apex_planet,
                    "interpretation": interpretation_text
                })
                planets_involved.update(all_planets)
        self.logger.debug(f"Found {len([p for p in patterns if p['type'] == 'Yod'])} Yods (after overlap check)." )
        # --- End Yod Detection ---
        
        # Analyze Grand Trine (TODO: Implement Grand Trine detection)
        # Requires finding three planets trining each other, often in the same element.
        
        # Analyze Grand Cross (TODO: Implement Grand Cross detection)
        # Requires finding four planets in a cross configuration (two oppositions, four squares).
        
        # Add other pattern analyses here (e.g., Mystic Rectangle, Kite)
        
        self.logger.debug(f"Found {len(patterns)} complex patterns in total.")
        return patterns
        
    def _analyze_combinations(self, birth_chart: Dict) -> List[Dict]:
        """Analyze significant planetary combinations (e.g., Sun-Moon blends).
        
        Args:
            birth_chart: Birth chart data
            
        Returns:
            List of dictionaries containing combination interpretations
        """
        self.logger.debug("Analyzing planetary combinations")
        combinations = []
        combinations_data = self.structured_data.get("combinations", {})
        sun_moon_combinations = combinations_data.get("sun_moon_combinations", {})
        
        planets = birth_chart.get("planets", {})
        sun_sign = None
        moon_sign = None
        
        # Handle dictionary format
        if isinstance(planets, dict):
            sun_sign = planets.get("Sun", {}).get("sign")
            moon_sign = planets.get("Moon", {}).get("sign")
        # Handle list format (backward compatibility)
        elif isinstance(planets, list):
            for planet in planets:
                if planet.get("name") == "Sun":
                    sun_sign = planet.get("sign")
                elif planet.get("name") == "Moon":
                    moon_sign = planet.get("sign")
                    
        if sun_sign and moon_sign:
            sun_sign_lower = sun_sign.lower()
            moon_sign_lower = moon_sign.lower()
            
            if sun_sign_lower in sun_moon_combinations and moon_sign_lower in sun_moon_combinations[sun_sign_lower]:
                interpretation = sun_moon_combinations[sun_sign_lower][moon_sign_lower]
                combinations.append({
                    "type": "Sun-Moon Combination",
                    "planets": ["Sun", "Moon"],
                    "signs": [sun_sign, moon_sign],
                    "interpretation": interpretation
                })
                self.logger.debug(f"Found Sun ({sun_sign})-Moon ({moon_sign}) combination interpretation.")
            else:
                self.logger.warning(f"No interpretation found for Sun ({sun_sign})-Moon ({moon_sign}) combination.")
        else:
            self.logger.warning("Sun or Moon sign missing, cannot analyze Sun-Moon combination.")
            
        # TODO: Add analysis for other combinations (Sun-Rising, Moon-Rising)
        
        self.logger.debug(f"Found {len(combinations)} planetary combinations")
        return combinations
