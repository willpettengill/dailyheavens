from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.models.interpretation import InterpretationRequest, InterpretationResponse

class InterpretationService:
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self._load_structured_data()

    def _load_structured_data(self):
        """Load structured data from JSON files."""
        structured_dir = self.data_dir / "structured"
        with open(structured_dir / "interpretation_templates.json", "r") as f:
            self.templates = json.load(f)
        with open(structured_dir / "astrological_techniques.json", "r") as f:
            self.techniques = json.load(f)
        with open(structured_dir / "planets.json", "r") as f:
            self.planets_data = json.load(f)
        with open(structured_dir / "signs.json", "r") as f:
            self.signs_data = json.load(f)
        with open(structured_dir / "houses.json", "r") as f:
            self.houses_data = json.load(f)
        with open(structured_dir / "aspects.json", "r") as f:
            self.aspects_data = json.load(f)
        with open(structured_dir / "planetary_dignities.json", "r") as f:
            self.dignities_data = json.load(f)
        with open(structured_dir / "descriptions.json", "r") as f:
            self.descriptions = json.load(f)
        with open(structured_dir / "interpretation_patterns.json", "r") as f:
            self.patterns = json.load(f)
        with open(structured_dir / "interpretation_combinations.json", "r") as f:
            self.combinations = json.load(f)

    def _get_planet_interpretation(self, planet: str, sign: str, house: int) -> str:
        """Get interpretation for a planet in a sign and house."""
        # Get house-planet combination interpretation
        house_planet_interp = self.templates["house_planet_combinations"].get(planet.lower(), {}).get(f"house{house}", "")
        
        # Get planet-sign interpretation
        planet_sign_template = self.templates["planet_sign_interpretations"]["format"]
        example_key = f"{planet.lower()}_in_{sign.lower()}"
        example_interp = self.templates["planet_sign_interpretations"]["examples"].get(example_key, "")
        
        if not example_interp:
            # Fallback to default qualities
            planet_qualities = {
                "Sun": "identity and self-expression",
                "Moon": "emotions and instincts",
                "Mercury": "communication and thinking",
                "Venus": "love and values",
                "Mars": "action and drive",
                "Jupiter": "growth and expansion",
                "Saturn": "discipline and responsibility",
                "Uranus": "innovation and change",
                "Neptune": "spirituality and imagination",
                "Pluto": "transformation and power"
            }
            sign_qualities = {
                "Aries": "pioneering and assertive energy",
                "Taurus": "stability and practicality",
                "Gemini": "adaptability and communication",
                "Cancer": "nurturing and emotional depth",
                "Leo": "creativity and self-expression",
                "Virgo": "analysis and service",
                "Libra": "harmony and relationships",
                "Scorpio": "intensity and transformation",
                "Sagittarius": "exploration and wisdom",
                "Capricorn": "ambition and structure",
                "Aquarius": "innovation and humanitarian ideals",
                "Pisces": "intuition and compassion"
            }
            example_interp = f"{planet_qualities.get(planet, '')} through {sign_qualities.get(sign, '')}"
        
        planet_sign_interp = planet_sign_template.format(
            planet=planet,
            sign=sign,
            interpretation=example_interp
        )
        
        return f"{planet_sign_interp}. {house_planet_interp}"

    def _get_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: str) -> str:
        """Get interpretation for an aspect between two planets."""
        aspect_key = f"{planet1.lower()}_{planet2.lower()}"
        aspect_type_map = {
            0: "conjunction",
            60: "sextile",
            90: "square",
            120: "trine",
            180: "opposition"
        }
        aspect_name = aspect_type_map.get(int(aspect_type))
        
        if aspect_name:
            aspect_interp = self.templates["aspect_interpretations"].get(aspect_key, {}).get(aspect_name)
            if aspect_interp:
                return aspect_interp
        
        # Fallback to generic aspect meanings
        aspect_meanings = {
            "conjunction": "combines and intensifies",
            "sextile": "creates opportunities and harmony",
            "square": "creates tension and growth",
            "trine": "flows naturally and supports",
            "opposition": "creates awareness and balance"
        }
        
        planet_qualities = {
            "Sun": "identity and vitality",
            "Moon": "emotions and instincts",
            "Mercury": "communication and thinking",
            "Venus": "love and values",
            "Mars": "action and drive",
            "Jupiter": "growth and opportunity",
            "Saturn": "structure and responsibility",
            "Uranus": "innovation and change",
            "Neptune": "inspiration and spirituality",
            "Pluto": "transformation and power",
            "MC": "career and public image",
            "ASC": "self-expression and personality"
        }
        
        planet1_quality = planet_qualities.get(planet1, "")
        planet2_quality = planet_qualities.get(planet2, "")
        aspect_meaning = aspect_meanings.get(aspect_name, "")
        
        return f"The {aspect_name} between {planet1} ({planet1_quality}) and {planet2} ({planet2_quality}) {aspect_meaning}."

    def _get_house_interpretation(self, house: int, sign: str) -> str:
        """Get interpretation for a house in a sign."""
        house_meanings = {
            1: "identity and self-image",
            2: "resources and values",
            3: "communication and learning",
            4: "home and emotional foundation",
            5: "creativity and self-expression",
            6: "work and health",
            7: "relationships and partnerships",
            8: "transformation and shared resources",
            9: "higher learning and philosophy",
            10: "career and public image",
            11: "groups and aspirations",
            12: "spirituality and unconscious"
        }
        
        sign_qualities = {
            "Aries": "pioneering and assertive energy",
            "Taurus": "stability and practicality",
            "Gemini": "adaptability and communication",
            "Cancer": "nurturing and emotional depth",
            "Leo": "creativity and self-expression",
            "Virgo": "analysis and service",
            "Libra": "harmony and relationships",
            "Scorpio": "intensity and transformation",
            "Sagittarius": "exploration and wisdom",
            "Capricorn": "ambition and structure",
            "Aquarius": "innovation and humanitarian ideals",
            "Pisces": "intuition and compassion"
        }
        
        house_meaning = house_meanings.get(house, "")
        sign_quality = sign_qualities.get(sign, "")
        
        return f"The {house}th house in {sign} indicates {house_meaning} expressed through {sign_quality}."

    def _get_special_configurations(self, birth_chart: Dict[str, Any]) -> List[str]:
        """Identify and interpret special configurations in the chart."""
        interpretations = []
        
        # Check for stelliums
        house_planets = {}
        sign_planets = {}
        for planet, data in birth_chart["planets"].items():
            house = data["house"]
            sign = data["sign"]
            house_planets.setdefault(house, []).append(planet)
            sign_planets.setdefault(sign, []).append(planet)
        
        # House themes
        house_themes = {
            1: "self-expression and personal identity",
            2: "resources, values, and material security",
            3: "communication, learning, and local environment",
            4: "home, family, and emotional foundation",
            5: "creativity, romance, and self-expression",
            6: "work, health, and daily routines",
            7: "relationships and partnerships",
            8: "transformation and shared resources",
            9: "higher learning, philosophy, and travel",
            10: "career, public image, and achievements",
            11: "groups, friendships, and future goals",
            12: "spirituality, unconscious, and hidden matters"
        }
        
        # Sign themes
        sign_themes = {
            "Aries": "initiative, leadership, and pioneering spirit",
            "Taurus": "stability, resources, and practical matters",
            "Gemini": "communication, versatility, and learning",
            "Cancer": "emotions, nurturing, and security",
            "Leo": "creativity, self-expression, and leadership",
            "Virgo": "analysis, service, and improvement",
            "Libra": "relationships, harmony, and balance",
            "Scorpio": "transformation, depth, and intensity",
            "Sagittarius": "expansion, wisdom, and adventure",
            "Capricorn": "ambition, structure, and achievement",
            "Aquarius": "innovation, groups, and humanitarian ideals",
            "Pisces": "spirituality, imagination, and compassion"
        }
        
        # House stelliums
        for house, planets in house_planets.items():
            if len(planets) >= 3:
                themes = house_themes.get(house, "various themes")
                interpretations.append(
                    f"A concentration of {len(planets)} planets ({', '.join(planets)}) in the {house}th house "
                    f"indicates a strong focus on {themes} in this lifetime."
                )
        
        # Sign stelliums
        for sign, planets in sign_planets.items():
            if len(planets) >= 3:
                themes = sign_themes.get(sign, "various qualities")
                interpretations.append(
                    f"A stellium of {len(planets)} planets ({', '.join(planets)}) in {sign} "
                    f"emphasizes {themes} in your life expression."
                )
        
        return interpretations

    def generate_interpretation(self, request: InterpretationRequest) -> InterpretationResponse:
        """Generate interpretation based on request parameters."""
        birth_chart = request.birth_chart
        area = request.area
        level = request.level
        
        interpretations = []
        
        # Add chart overview
        sun_data = birth_chart["planets"].get("Sun", {})
        asc_data = birth_chart["angles"].get("Asc", {})
        if sun_data and asc_data:
            overview_template = self.templates["reading_structure"]["overview"]["template"]
            interpretations.append(overview_template.format(
                sun_sign=sun_data["sign"],
                ascendant_sign=asc_data["sign"],
                personality_blend=f"{sun_data['sign']} and {asc_data['sign']}",
                chart_ruler="Mars" if asc_data["sign"] == "Scorpio" else "Venus",  # Simplified ruler assignment
                chart_ruler_house=sun_data["house"],
                chart_ruler_interpretation="focus on personal resources and values"  # Simplified interpretation
            ))
            
            # Add Sun sign description
            sun_sign = sun_data["sign"].lower()
            interpretations.append(self.descriptions[sun_sign]["sun_sign"])
            
            # Add Moon sign description
            moon_data = birth_chart["planets"].get("Moon", {})
            if moon_data:
                moon_sign = moon_data["sign"].lower()
                interpretations.append(self.descriptions[moon_sign]["moon_sign"])
            
            # Add Rising sign description
            rising_sign = asc_data["sign"].lower()
            interpretations.append(self.descriptions[rising_sign]["rising_sign"])
        
        # Add elemental pattern analysis
        elemental_analysis = self._analyze_elemental_patterns(birth_chart)
        if elemental_analysis:
            interpretations.append(elemental_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.extend([
                    f"Strengths: {', '.join(elemental_analysis['interpretation']['strengths'])}",
                    f"Challenges: {', '.join(elemental_analysis['interpretation']['challenges'])}"
                ])
        
        # Add modality pattern analysis
        modality_analysis = self._analyze_modality_patterns(birth_chart)
        if modality_analysis:
            interpretations.append(modality_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.extend([
                    f"Strengths: {', '.join(modality_analysis['interpretation']['strengths'])}",
                    f"Challenges: {', '.join(modality_analysis['interpretation']['challenges'])}"
                ])
        
        # Add Sun-Moon combination analysis
        sun_moon_analysis = self._analyze_sun_moon_combination(birth_chart)
        if sun_moon_analysis:
            interpretations.append(sun_moon_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.append(sun_moon_analysis["interpretation"]["interpretation"])
        
        # Add Sun-Rising combination analysis
        sun_rising_analysis = self._analyze_sun_rising_combination(birth_chart)
        if sun_rising_analysis:
            interpretations.append(sun_rising_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.append(sun_rising_analysis["interpretation"]["interpretation"])
        
        # Add Moon-Rising combination analysis
        moon_rising_analysis = self._analyze_moon_rising_combination(birth_chart)
        if moon_rising_analysis:
            interpretations.append(moon_rising_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.append(moon_rising_analysis["interpretation"]["interpretation"])
        
        # Add house emphasis analysis
        house_emphasis_analysis = self._analyze_house_emphasis(birth_chart)
        if house_emphasis_analysis:
            interpretations.append(house_emphasis_analysis["interpretation"]["description"])
            if level == "detailed":
                interpretations.append(f"Focus areas: {', '.join(house_emphasis_analysis['interpretation']['focus'])}")
        
        # Add special configurations
        special_configs = self._get_special_configurations(birth_chart)
        if special_configs:
            interpretations.extend(special_configs)
        
        # Add area-specific interpretations
        if area == "career":
            interpretations.extend(self._interpret_career(birth_chart, level))
        elif area == "relationships":
            interpretations.extend(self._interpret_relationships(birth_chart, level))
        elif area == "health":
            interpretations.extend(self._interpret_health(birth_chart, level))
        elif area == "spirituality":
            interpretations.extend(self._interpret_spirituality(birth_chart, level))
        elif area == "personal_growth":
            interpretations.extend(self._interpret_personal_growth(birth_chart, level))
        
        return InterpretationResponse(
            status="success",
            data={
                "interpretations": interpretations,
                "patterns": {
                    "elemental": elemental_analysis,
                    "modality": modality_analysis,
                    "sun_moon": sun_moon_analysis,
                    "sun_rising": sun_rising_analysis,
                    "moon_rising": moon_rising_analysis,
                    "house_emphasis": house_emphasis_analysis
                },
                "techniques_used": self.techniques.get(area, [])
            }
        )

    def _interpret_career(self, birth_chart: Dict[str, Any], level: str) -> List[str]:
        """Generate career-related interpretations."""
        interpretations = []
        
        # Analyze Sun position
        sun = birth_chart["planets"].get("Sun")
        if sun:
            interpretations.append(self._get_planet_interpretation(
                "Sun", sun["sign"], sun["house"]
            ))
            
        # Analyze 10th house
        mc = birth_chart["angles"].get("MC")
        if mc:
            interpretations.append(self._get_house_interpretation(
                10, mc["sign"]
            ))
            
        # Analyze aspects to MC
        for planet, data in birth_chart["planets"].items():
            for aspect in data.get("aspects", []):
                if aspect["planet"] == "MC":
                    interpretations.append(self._get_aspect_interpretation(
                        planet, "MC", aspect["type"]
                    ))
        
        return interpretations

    def _interpret_relationships(self, birth_chart: Dict[str, Any], level: str) -> List[str]:
        """Generate relationship-related interpretations."""
        interpretations = []
        
        # Analyze Venus position
        venus = birth_chart["planets"].get("Venus")
        if venus:
            interpretations.append(self._get_planet_interpretation(
                "Venus", venus["sign"], venus["house"]
            ))
            
        # Analyze 7th house
        desc = birth_chart["angles"].get("DESC")
        if desc:
            interpretations.append(self._get_house_interpretation(
                7, desc["sign"]
            ))
            
        # Analyze aspects to Venus
        for planet, data in birth_chart["planets"].items():
            for aspect in data.get("aspects", []):
                if aspect["planet"] == "Venus":
                    interpretations.append(self._get_aspect_interpretation(
                        planet, "Venus", aspect["type"]
                    ))
        
        return interpretations

    def _interpret_health(self, birth_chart: Dict[str, Any], level: str) -> List[str]:
        """Generate health-related interpretations."""
        interpretations = []
        
        # Analyze Mars position
        mars = birth_chart["planets"].get("Mars")
        if mars:
            interpretations.append(self._get_planet_interpretation(
                "Mars", mars["sign"], mars["house"]
            ))
            
        # Analyze 6th house
        house6 = birth_chart["houses"].get(6)
        if house6:
            interpretations.append(self._get_house_interpretation(
                6, house6["sign"]
            ))
            
        # Analyze aspects to Mars
        for planet, data in birth_chart["planets"].items():
            for aspect in data.get("aspects", []):
                if aspect["planet"] == "Mars":
                    interpretations.append(self._get_aspect_interpretation(
                        planet, "Mars", aspect["type"]
                    ))
        
        return interpretations

    def _interpret_spirituality(self, birth_chart: Dict[str, Any], level: str) -> List[str]:
        """Generate spirituality-related interpretations."""
        interpretations = []
        
        # Analyze Neptune position
        neptune = birth_chart["planets"].get("Neptune")
        if neptune:
            interpretations.append(self._get_planet_interpretation(
                "Neptune", neptune["sign"], neptune["house"]
            ))
            
        # Analyze 12th house
        house12 = birth_chart["houses"].get(12)
        if house12:
            interpretations.append(self._get_house_interpretation(
                12, house12["sign"]
            ))
            
        # Analyze aspects to Neptune
        for planet, data in birth_chart["planets"].items():
            for aspect in data.get("aspects", []):
                if aspect["planet"] == "Neptune":
                    interpretations.append(self._get_aspect_interpretation(
                        planet, "Neptune", aspect["type"]
                    ))
        
        return interpretations

    def _interpret_personal_growth(self, birth_chart: Dict[str, Any], level: str) -> List[str]:
        """Generate personal growth-related interpretations."""
        interpretations = []
        
        # Analyze Moon position
        moon = birth_chart["planets"].get("Moon")
        if moon:
            interpretations.append(self._get_planet_interpretation(
                "Moon", moon["sign"], moon["house"]
            ))
            
        # Analyze 1st house
        asc = birth_chart["angles"].get("ASC")
        if asc:
            interpretations.append(self._get_house_interpretation(
                1, asc["sign"]
            ))
            
        # Analyze aspects to Moon
        for planet, data in birth_chart["planets"].items():
            for aspect in data.get("aspects", []):
                if aspect["planet"] == "Moon":
                    interpretations.append(self._get_aspect_interpretation(
                        planet, "Moon", aspect["type"]
                    ))
        
        return interpretations

    def _analyze_elemental_patterns(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze elemental patterns in the chart."""
        elements = {
            "fire": ["Aries", "Leo", "Sagittarius"],
            "earth": ["Taurus", "Virgo", "Capricorn"],
            "air": ["Gemini", "Libra", "Aquarius"],
            "water": ["Cancer", "Scorpio", "Pisces"]
        }
        
        element_counts = {element: 0 for element in elements}
        
        # Count planets in each element
        for planet_data in birth_chart["planets"].values():
            sign = planet_data["sign"]
            for element, signs in elements.items():
                if sign in signs:
                    element_counts[element] += 1
                    break
        
        # Determine dominant element
        max_count = max(element_counts.values())
        dominant_elements = [element for element, count in element_counts.items() if count == max_count]
        
        return {
            "counts": element_counts,
            "dominant": dominant_elements,
            "interpretation": self.patterns["elemental_patterns"][f"{dominant_elements[0]}_dominant"]
        }

    def _analyze_modality_patterns(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze modality patterns in the chart."""
        modalities = {
            "cardinal": ["Aries", "Cancer", "Libra", "Capricorn"],
            "fixed": ["Taurus", "Leo", "Scorpio", "Aquarius"],
            "mutable": ["Gemini", "Virgo", "Sagittarius", "Pisces"]
        }
        
        modality_counts = {modality: 0 for modality in modalities}
        
        # Count planets in each modality
        for planet_data in birth_chart["planets"].values():
            sign = planet_data["sign"]
            for modality, signs in modalities.items():
                if sign in signs:
                    modality_counts[modality] += 1
                    break
        
        # Determine dominant modality
        max_count = max(modality_counts.values())
        dominant_modalities = [modality for modality, count in modality_counts.items() if count == max_count]
        
        return {
            "counts": modality_counts,
            "dominant": dominant_modalities,
            "interpretation": self.patterns["modality_patterns"][f"{dominant_modalities[0]}_dominant"]
        }

    def _analyze_sun_moon_combination(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the combination of Sun and Moon signs."""
        sun_data = birth_chart["planets"].get("Sun", {})
        moon_data = birth_chart["planets"].get("Moon", {})
        
        if not sun_data or not moon_data:
            return None
            
        sun_sign = sun_data["sign"]
        moon_sign = moon_data["sign"]
        
        # Get elements of both signs
        elements = {
            "fire": ["Aries", "Leo", "Sagittarius"],
            "earth": ["Taurus", "Virgo", "Capricorn"],
            "air": ["Gemini", "Libra", "Aquarius"],
            "water": ["Cancer", "Scorpio", "Pisces"]
        }
        
        sun_element = None
        moon_element = None
        for element, signs in elements.items():
            if sun_sign in signs:
                sun_element = element
            if moon_sign in signs:
                moon_element = element
                
        if sun_element == moon_element:
            combination_type = "same_element"
        elif (sun_element in ["fire", "air"] and moon_element in ["fire", "air"]) or \
             (sun_element in ["earth", "water"] and moon_element in ["earth", "water"]):
            combination_type = "compatible_elements"
        else:
            combination_type = "incompatible_elements"
            
        return {
            "sun_sign": sun_sign,
            "moon_sign": moon_sign,
            "combination_type": combination_type,
            "interpretation": self.combinations["sun_moon_combinations"][combination_type]
        }

    def _analyze_sun_rising_combination(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the combination of Sun and Rising signs."""
        sun_data = birth_chart["planets"].get("Sun", {})
        asc_data = birth_chart["angles"].get("Asc", {})
        
        if not sun_data or not asc_data:
            return None
            
        sun_sign = sun_data["sign"]
        rising_sign = asc_data["sign"]
        
        if sun_sign == rising_sign:
            combination_type = "same_sign"
        elif sun_sign in self.signs_data[rising_sign]["compatible_signs"]:
            combination_type = "compatible_signs"
        else:
            combination_type = "challenging_signs"
            
        return {
            "sun_sign": sun_sign,
            "rising_sign": rising_sign,
            "combination_type": combination_type,
            "interpretation": self.combinations["sun_rising_combinations"][combination_type]
        }

    def _analyze_moon_rising_combination(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the combination of Moon and Rising signs."""
        moon_data = birth_chart["planets"].get("Moon", {})
        asc_data = birth_chart["angles"].get("Asc", {})
        
        if not moon_data or not asc_data:
            return None
            
        moon_sign = moon_data["sign"]
        rising_sign = asc_data["sign"]
        
        if moon_sign == rising_sign:
            combination_type = "same_sign"
        elif moon_sign in self.signs_data[rising_sign]["compatible_signs"]:
            combination_type = "compatible_signs"
        else:
            combination_type = "challenging_signs"
            
        return {
            "moon_sign": moon_sign,
            "rising_sign": rising_sign,
            "combination_type": combination_type,
            "interpretation": self.combinations["moon_rising_combinations"][combination_type]
        }

    def _analyze_house_emphasis(self, birth_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze house emphasis in the chart."""
        house_counts = {i: 0 for i in range(1, 13)}
        
        # Count planets in each house
        for planet_data in birth_chart["planets"].values():
            house = planet_data["house"]
            house_counts[house] += 1
            
        # Determine house emphasis
        max_count = max(house_counts.values())
        emphasized_houses = [house for house, count in house_counts.items() if count == max_count]
        
        # Categorize houses
        house_categories = {
            "angular": [1, 4, 7, 10],
            "succedent": [2, 5, 8, 11],
            "cadent": [3, 6, 9, 12]
        }
        
        category_counts = {category: 0 for category in house_categories}
        for house in emphasized_houses:
            for category, houses in house_categories.items():
                if house in houses:
                    category_counts[category] += 1
                    break
                    
        # Determine dominant category
        max_category_count = max(category_counts.values())
        dominant_categories = [category for category, count in category_counts.items() if count == max_category_count]
        
        return {
            "house_counts": house_counts,
            "emphasized_houses": emphasized_houses,
            "category_counts": category_counts,
            "dominant_categories": dominant_categories,
            "interpretation": self.patterns["house_emphasis"][dominant_categories[0]]
        } 