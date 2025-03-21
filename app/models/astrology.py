from enum import Enum
from typing import Dict, List, Any, Optional


class Element(Enum):
    FIRE = "fire"
    EARTH = "earth"
    AIR = "air"
    WATER = "water"
    
    def __str__(self):
        return self.value


class Modality(Enum):
    CARDINAL = "cardinal"
    FIXED = "fixed"
    MUTABLE = "mutable"
    
    def __str__(self):
        return self.value


class AspectType(Enum):
    CONJUNCTION = "conjunction"
    SEXTILE = "sextile"
    SQUARE = "square"
    TRINE = "trine"
    OPPOSITION = "opposition"
    QUINCUNX = "quincunx"
    
    @property
    def nature(self) -> str:
        if self in [AspectType.CONJUNCTION, AspectType.SEXTILE, AspectType.TRINE]:
            return "harmonious"
        elif self in [AspectType.SQUARE, AspectType.OPPOSITION, AspectType.QUINCUNX]:
            return "challenging"
        return "neutral"
    
    @property
    def type(self) -> str:
        return self.value
    
    @property
    def keywords(self) -> List[str]:
        aspect_keywords = {
            AspectType.CONJUNCTION: ["unity", "focus", "intensity"],
            AspectType.SEXTILE: ["opportunity", "flow", "harmony"],
            AspectType.SQUARE: ["tension", "challenge", "growth"],
            AspectType.TRINE: ["harmony", "flow", "creativity"],
            AspectType.OPPOSITION: ["balance", "awareness", "relationship"],
            AspectType.QUINCUNX: ["adjustment", "integration", "adaptation"],
        }
        return aspect_keywords.get(self, [])


class Dignity(Enum):
    DOMICILE = "domicile"
    EXALTATION = "exaltation"
    DETRIMENT = "detriment"
    FALL = "fall"
    
    def __str__(self):
        return self.value


class HouseType(Enum):
    ANGULAR = "angular"
    SUCCEDENT = "succedent"
    CADENT = "cadent"
    
    @staticmethod
    def get_type(house_number: int) -> 'HouseType':
        if house_number in [1, 4, 7, 10]:
            return HouseType.ANGULAR
        elif house_number in [2, 5, 8, 11]:
            return HouseType.SUCCEDENT
        else:
            return HouseType.CADENT


class Sign:
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"
    
    _data = {
        ARIES: {"element": Element.FIRE, "modality": Modality.CARDINAL},
        TAURUS: {"element": Element.EARTH, "modality": Modality.FIXED},
        GEMINI: {"element": Element.AIR, "modality": Modality.MUTABLE},
        CANCER: {"element": Element.WATER, "modality": Modality.CARDINAL},
        LEO: {"element": Element.FIRE, "modality": Modality.FIXED},
        VIRGO: {"element": Element.EARTH, "modality": Modality.MUTABLE},
        LIBRA: {"element": Element.AIR, "modality": Modality.CARDINAL},
        SCORPIO: {"element": Element.WATER, "modality": Modality.FIXED},
        SAGITTARIUS: {"element": Element.FIRE, "modality": Modality.MUTABLE},
        CAPRICORN: {"element": Element.EARTH, "modality": Modality.CARDINAL},
        AQUARIUS: {"element": Element.AIR, "modality": Modality.FIXED},
        PISCES: {"element": Element.WATER, "modality": Modality.MUTABLE},
    }
    
    @classmethod
    def get_element(cls, sign: str) -> Element:
        return cls._data.get(sign, {}).get("element", Element.FIRE)
    
    @classmethod
    def get_modality(cls, sign: str) -> Modality:
        return cls._data.get(sign, {}).get("modality", Modality.CARDINAL)
    
    @classmethod
    def get_qualities(cls, sign: str) -> Dict[str, str]:
        # Default qualities for testing
        return {"general": "general qualities"}
    
    @classmethod
    def get_keywords(cls, sign: str) -> List[str]:
        # Default keywords for testing
        return ["keyword1", "keyword2"]


class Planet:
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"
    
    @classmethod
    def get_qualities(cls, planet: str) -> Dict[str, str]:
        # Default qualities for testing
        return {"general": "general qualities"}
    
    @classmethod
    def get_keywords(cls, planet: str) -> List[str]:
        # Default keywords for testing
        return ["keyword1", "keyword2"]
    
    @classmethod
    def get_dignities(cls, planet: str) -> Dict[str, List[str]]:
        # Default dignities for testing
        return {
            "domicile": [],
            "exaltation": [],
            "detriment": [],
            "fall": []
        }


class House:
    @staticmethod
    def get_qualities(house_number: int) -> Dict[str, str]:
        # Default qualities for testing
        return {"general": f"House {house_number} qualities"}
    
    @staticmethod
    def get_keywords(house_number: int) -> List[str]:
        # Default keywords for testing
        return [f"house{house_number}_keyword1", f"house{house_number}_keyword2"]


class Aspect:
    @staticmethod
    def get_type(aspect_name: str) -> AspectType:
        try:
            return AspectType[aspect_name.upper()]
        except (KeyError, AttributeError):
            return AspectType.CONJUNCTION 