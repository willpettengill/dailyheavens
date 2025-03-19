import json
from pathlib import Path
from typing import List, Dict, Any

from app.models.interpretation import InterpretationLevel, InterpretationArea


class InterpretationService:
    def __init__(self):
        self.structured_data_path = Path("data/structured")
        self._load_structured_data()

    def _load_structured_data(self):
        """Load all structured JSON data files."""
        self.templates = self._load_json_file("interpretation_templates.json")
        self.signs = self._load_json_file("signs.json")
        self.houses = self._load_json_file("houses.json")
        self.aspects = self._load_json_file("aspects.json")
        self.planetary_dignities = self._load_json_file("planetary_dignities.json")
        self.house_systems = self._load_json_file("house_systems.json")
        self.astrological_techniques = self._load_json_file("astrological_techniques.json")

    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the structured data directory."""
        file_path = self.structured_data_path / filename
        with open(file_path, 'r') as f:
            return json.load(f)

    def generate_interpretation(
        self,
        birth_chart_data: dict,
        level: InterpretationLevel,
        areas: List[InterpretationArea],
        include_transits: bool = False,
        language_style: str = "professional"
    ) -> dict:
        """Generate a complete astrological interpretation based on the birth chart data."""
        
        # Extract key chart components
        planets = birth_chart_data.get("planets", {})
        houses = birth_chart_data.get("houses", {})
        angles = birth_chart_data.get("angles", {})
        aspects = birth_chart_data.get("aspects", [])

        # Initialize interpretation data
        interpretation = {
            "overview": self._generate_overview(planets, angles),
            "personality": self._generate_personality_analysis(planets, houses, angles),
            "areas": {},
            "special_patterns": self._identify_special_patterns(planets, aspects)
        }

        # Generate interpretations for requested areas
        for area in areas:
            interpretation["areas"][area] = self._interpret_area(
                area, planets, houses, aspects, level
            )

        # Add transit interpretations if requested
        if include_transits:
            interpretation["transits"] = self._interpret_transits(birth_chart_data)

        return interpretation

    def _generate_overview(self, planets: dict, angles: dict) -> dict:
        """Generate an overview of the birth chart."""
        sun_sign = planets.get("Sun", {}).get("sign")
        ascendant_sign = angles.get("Asc", {}).get("sign")
        
        # Get chart ruler based on Ascendant sign
        chart_ruler = self._get_chart_ruler(ascendant_sign)
        chart_ruler_house = planets.get(chart_ruler, {}).get("house")

        # Use template to generate overview
        template = self.templates["reading_structure"]["overview"]["template"]
        overview = template.format(
            sun_sign=sun_sign,
            ascendant_sign=ascendant_sign,
            personality_blend=self._blend_sun_ascendant(sun_sign, ascendant_sign),
            chart_ruler=chart_ruler,
            chart_ruler_house=chart_ruler_house,
            chart_ruler_interpretation=self._interpret_planet_in_house(chart_ruler, chart_ruler_house)
        )

        return {
            "text": overview,
            "key_points": {
                "sun_sign": sun_sign,
                "ascendant": ascendant_sign,
                "chart_ruler": chart_ruler,
                "chart_ruler_house": chart_ruler_house
            }
        }

    def _generate_personality_analysis(self, planets: dict, houses: dict, angles: dict) -> dict:
        """Generate a detailed personality analysis."""
        sun_data = planets.get("Sun", {})
        moon_data = planets.get("Moon", {})
        ascendant_data = angles.get("Asc", {})

        template = self.templates["reading_structure"]["personality"]["template"]
        analysis = template.format(
            sun_sign=sun_data.get("sign"),
            sun_house=sun_data.get("house"),
            sun_house_themes=self._get_house_themes(sun_data.get("house")),
            ascendant_sign=ascendant_data.get("sign"),
            ascendant_qualities=self._get_sign_qualities(ascendant_data.get("sign")),
            moon_sign=moon_data.get("sign"),
            moon_house=moon_data.get("house"),
            moon_interpretation=self._interpret_moon_placement(moon_data)
        )

        return {
            "text": analysis,
            "components": {
                "sun": sun_data,
                "moon": moon_data,
                "ascendant": ascendant_data
            }
        }

    def _identify_special_patterns(self, planets: dict, aspects: list) -> dict:
        """Identify and interpret special chart patterns."""
        patterns = {
            "stelliums": self._find_stelliums(planets),
            "aspect_patterns": self._find_aspect_patterns(aspects)
        }
        
        return patterns

    def _interpret_area(
        self,
        area: InterpretationArea,
        planets: dict,
        houses: dict,
        aspects: list,
        level: InterpretationLevel
    ) -> dict:
        """Generate interpretation for a specific life area."""
        area_interpretations = {
            InterpretationArea.CAREER: self._interpret_career(planets, houses, aspects, level),
            InterpretationArea.RELATIONSHIPS: self._interpret_relationships(planets, houses, aspects, level),
            InterpretationArea.PERSONAL_GROWTH: self._interpret_personal_growth(planets, houses, aspects, level),
            # Add other area interpretations as needed
        }
        
        return area_interpretations.get(area, {"text": "Area interpretation not implemented"})

    def _get_chart_ruler(self, ascendant_sign: str) -> str:
        """Get the ruling planet of the Ascendant sign."""
        for planet, ruled_signs in self.planetary_dignities["dignities"]["rulership"].items():
            if ascendant_sign in ruled_signs:
                return planet
        return "Unknown"

    def _blend_sun_ascendant(self, sun_sign: str, ascendant_sign: str) -> str:
        """Create a description of the personality blend between Sun and Ascendant signs."""
        sun_qualities = self.signs[sun_sign.lower()]["qualities"][:3]
        asc_qualities = self.signs[ascendant_sign.lower()]["qualities"][:3]
        
        return f"{', '.join(sun_qualities)} with a {', '.join(asc_qualities)} approach"

    def _get_house_themes(self, house_number: int) -> str:
        """Get the main themes of a house."""
        house_key = f"house{house_number}"
        return self.houses[house_key]["qualities"][0]

    def _get_sign_qualities(self, sign: str) -> str:
        """Get the main qualities of a sign."""
        return ", ".join(self.signs[sign.lower()]["qualities"][:3])

    def _interpret_moon_placement(self, moon_data: dict) -> str:
        """Interpret the Moon's placement in sign and house."""
        sign = moon_data.get("sign", "").lower()
        house = moon_data.get("house")
        
        sign_qualities = self.signs[sign]["qualities"][:2]
        house_themes = self._get_house_themes(house)
        
        return f"{', '.join(sign_qualities)} in matters of {house_themes}"

    def _find_stelliums(self, planets: dict) -> list:
        """Find stelliums (3 or more planets in the same sign or house)."""
        sign_groups = {}
        house_groups = {}
        
        for planet, data in planets.items():
            sign = data.get("sign")
            house = data.get("house")
            
            if sign:
                sign_groups.setdefault(sign, []).append(planet)
            if house:
                house_groups.setdefault(house, []).append(planet)
        
        stelliums = []
        for sign, planets_list in sign_groups.items():
            if len(planets_list) >= 3:
                stelliums.append({
                    "type": "sign",
                    "location": sign,
                    "planets": planets_list
                })
        
        for house, planets_list in house_groups.items():
            if len(planets_list) >= 3:
                stelliums.append({
                    "type": "house",
                    "location": house,
                    "planets": planets_list
                })
        
        return stelliums

    def _find_aspect_patterns(self, aspects: list) -> list:
        """Identify major aspect patterns (grand trines, T-squares, etc.)."""
        # This is a placeholder for more complex aspect pattern detection
        patterns = []
        # Implementation would involve graph theory to detect patterns
        return patterns

    def _interpret_planet_in_house(self, planet: str, house: int) -> str:
        """Interpret a planet's placement in a house."""
        house_key = f"house{house}"
        if planet in self.templates["house_planet_combinations"]:
            return self.templates["house_planet_combinations"][planet][house_key]
        return f"focus on {self.houses[house_key]['qualities'][0]}"

    # Area-specific interpretation methods
    def _interpret_career(self, planets: dict, houses: dict, aspects: list, level: InterpretationLevel) -> dict:
        """Generate career-focused interpretation."""
        # Implementation would focus on 2nd, 6th, and 10th houses, plus relevant planets
        return {"text": "Career interpretation placeholder"}

    def _interpret_relationships(self, planets: dict, houses: dict, aspects: list, level: InterpretationLevel) -> dict:
        """Generate relationship-focused interpretation."""
        # Implementation would focus on 5th, 7th, and 8th houses, plus Venus/Mars aspects
        return {"text": "Relationships interpretation placeholder"}

    def _interpret_personal_growth(self, planets: dict, houses: dict, aspects: list, level: InterpretationLevel) -> dict:
        """Generate personal growth-focused interpretation."""
        # Implementation would focus on 1st, 9th, and 12th houses, plus outer planets
        return {"text": "Personal growth interpretation placeholder"}

    def _interpret_transits(self, birth_chart_data: dict) -> dict:
        """Interpret current transits to the natal chart."""
        # This would require current planetary positions to be passed in
        return {"text": "Transit interpretation placeholder"} 