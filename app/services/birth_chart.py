from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects

from app.core.config import settings

# Define the list of planets we want to calculate
PLANETS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]

class BirthChartService:
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self._load_structured_data()

    def _load_structured_data(self):
        """Load structured data from JSON files."""
        structured_dir = self.data_dir / "structured"
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

    def _get_house_number(self, chart: Chart, longitude: float) -> int:
        """Get the house number for a given longitude."""
        for i in range(1, 13):
            house = chart.get(f"House{i}")
            next_house = chart.get(f"House{(i % 12) + 1}")
            if (house.lon <= longitude < next_house.lon) or \
               (house.lon > next_house.lon and (longitude >= house.lon or longitude < next_house.lon)):
                return i
        return 1  # Default to first house if not found

    def _get_planet_data(self, obj: Any, chart: Chart) -> Dict[str, Any]:
        """Extract all available data for a planet."""
        house_num = self._get_house_number(chart, obj.lon)
        
        # Get aspects with other planets
        planet_aspects = []
        for other_planet in PLANETS:
            if other_planet != obj.id:
                other_obj = chart.get(other_planet)
                aspect = aspects.getAspect(obj, other_obj, const.MAJOR_ASPECTS)
                if aspect:
                    planet_aspects.append({
                        "planet": other_planet,
                        "type": aspect.type,
                        "orb": aspect.orb,
                        "qualities": self.aspects_data.get(aspect.type, {})
                    })
        
        # Get planet data from structured data
        planet_data = self.planets_data.get(obj.id, {})
        sign_data = self.signs_data.get(obj.sign, {})
        house_data = self.houses_data.get(str(house_num), {})
        
        return {
            "name": obj.id,
            "longitude": obj.lon,
            "latitude": obj.lat,
            "sign": obj.sign,
            "sign_longitude": obj.signlon,
            "house": house_num,
            "movement": obj.movement(),
            "element": obj.element(),
            "is_direct": obj.isDirect(),
            "is_retrograde": obj.isRetrograde(),
            "aspects": planet_aspects,
            "qualities": planet_data,
            "sign_qualities": sign_data,
            "house_qualities": house_data,
            "dignities": self.dignities_data.get(obj.id, {})
        }

    def calculate_birth_chart(self, date_of_birth: datetime, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate birth chart using flatlib."""
        # Convert datetime to flatlib format (YYYY/MM/DD HH:mm)
        date_str = date_of_birth.strftime("%Y/%m/%d")
        time_str = date_of_birth.strftime("%H:%M")
        date = Datetime(f"{date_str}", f"{time_str}")
        pos = GeoPos(latitude, longitude)
        
        # Create chart
        chart = Chart(date, pos)
        
        # Extract planetary positions with all available data
        planets = {}
        for planet in PLANETS:
            obj = chart.get(planet)
            planets[planet] = self._get_planet_data(obj, chart)
        
        # Extract house cusps with all available data
        houses = {}
        for i in range(1, 13):
            house = chart.get(f"House{i}")
            house_data = self.houses_data.get(str(i), {})
            houses[i] = {
                "longitude": house.lon,
                "sign": house.sign,
                "sign_longitude": house.signlon,
                "qualities": house_data
            }
        
        # Get angles with all available data
        angles = {}
        for angle in [const.ASC, const.MC, const.DESC, const.IC]:
            obj = chart.get(angle)
            sign_data = self.signs_data.get(obj.sign, {})
            angles[angle] = {
                "longitude": obj.lon,
                "sign": obj.sign,
                "sign_longitude": obj.signlon,
                "qualities": sign_data
            }
        
        return {
            "planets": planets,
            "houses": houses,
            "angles": angles
        } 