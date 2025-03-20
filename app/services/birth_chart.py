import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects as flatlib_aspects

from app.core.config import settings

logger = logging.getLogger(__name__)

# Define the list of planets we want to calculate
PLANETS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]

class BirthChartService:
    """Service for calculating and analyzing birth charts."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent
        else:
            self.data_dir = Path(data_dir)
            
        self.planets = [
            const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
            const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
        ]
        self._load_structured_data()

    def _load_structured_data(self):
        """Load structured data from JSON files."""
        try:
            structured_dir = self.data_dir / "data" / "structured"
            if not structured_dir.exists():
                logger.warning(f"Structured data directory not found: {structured_dir}")
                return
            
            # Load planet data
            planet_file = structured_dir / "planets.json"
            if planet_file.exists():
                with open(planet_file) as f:
                    self.planets_data = json.load(f)
            else:
                logger.warning(f"Planet data file not found: {planet_file}")
                self.planets_data = {}
            
            # Load house data
            house_file = structured_dir / "houses.json"
            if house_file.exists():
                with open(house_file) as f:
                    self.houses_data = json.load(f)
            else:
                logger.warning(f"House data file not found: {house_file}")
                self.houses_data = {}
            
            # Load sign data
            sign_file = structured_dir / "signs.json"
            if sign_file.exists():
                with open(sign_file) as f:
                    self.signs_data = json.load(f)
            else:
                logger.warning(f"Sign data file not found: {sign_file}")
                self.signs_data = {}
            
            # Load aspect data
            aspect_file = structured_dir / "aspects.json"
            if aspect_file.exists():
                with open(aspect_file) as f:
                    self.aspects_data = json.load(f)
            else:
                logger.warning(f"Aspect data file not found: {aspect_file}")
                self.aspects_data = {}
            
            # Load dignities data
            dignities_file = structured_dir / "dignities.json"
            if dignities_file.exists():
                with open(dignities_file) as f:
                    self.dignities_data = json.load(f)
            else:
                logger.warning(f"Dignities data file not found: {dignities_file}")
                self.dignities_data = {}
            
            logger.info(f"Successfully loaded structured data from {structured_dir}")
            
        except Exception as e:
            logger.error(f"Error loading structured data: {str(e)}")
            raise

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
                aspect = flatlib_aspects.getAspect(obj, other_obj, const.MAJOR_ASPECTS)
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

    def calculate_birth_chart(self, date_of_birth: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate a birth chart for the given date and location."""
        try:
            # Validate date format and range
            try:
                if isinstance(date_of_birth, str):
                    date = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
                else:
                    date = date_of_birth
                    
                # Check if date is reasonable (not too far in past or future)
                current_year = datetime.now().year
                if date.year < 1900 or date.year > current_year + 1:
                    return {
                        "status": "error",
                        "error": f"Date must be between 1900 and {current_year + 1}"
                    }
            except ValueError:
                return {
                    "status": "error",
                    "error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }
                
            # Format date for flatlib
            date_str = date.strftime("%Y/%m/%d")
            time_str = date.strftime("%H:%M")
            flatlib_date = Datetime(date_str, time_str, '+00:00')
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                return {
                    "status": "error",
                    "error": "Latitude must be between -90 and 90 degrees"
                }
            if not (-180 <= longitude <= 180):
                return {
                    "status": "error",
                    "error": "Longitude must be between -180 and 180 degrees"
                }
            
            # Create flatlib chart
            pos = GeoPos(float(latitude), float(longitude))
            chart = Chart(flatlib_date, pos)
            
            # Extract planetary positions with validation
            planets = {}
            for planet in self.planets:
                try:
                    obj = chart.get(planet)
                    if obj:
                        house_num = self._get_house_number(chart, obj.lon)
                        planets[planet] = {
                            "sign": obj.sign,
                            "degree": round(obj.lon, 2),  # Round to 2 decimal places
                            "house": house_num,
                            "retrograde": obj.isRetrograde() if hasattr(obj, 'isRetrograde') else False
                        }
                except KeyError:
                    logger.warning(f"Planet {planet} not found in chart")
                    continue
            
            # Validate minimum required planets
            required_planets = ["Sun", "Moon", "Ascendant"]
            missing_planets = [p for p in required_planets if p not in planets]
            if missing_planets:
                return {
                    "status": "error",
                    "error": f"Missing required planets: {', '.join(missing_planets)}"
                }
            
            # Extract house cusps with validation
            houses = {}
            for i in range(1, 13):
                try:
                    house = chart.getHouse(i)
                    houses[str(i)] = {
                        "sign": house.sign,
                        "degree": round(house.lon, 2)  # Round to 2 decimal places
                    }
                except (KeyError, AttributeError):
                    logger.warning(f"House {i} not found in chart")
                    continue
            
            # Validate minimum required houses
            if len(houses) < 10:  # Allow some flexibility but require most houses
                return {
                    "status": "error",
                    "error": "Insufficient house data calculated"
                }
            
            # Extract angles with validation
            angles = {}
            for angle in ["ASC", "MC"]:
                try:
                    obj = chart.get(getattr(const, angle))
                    angles[angle] = {
                        "sign": obj.sign,
                        "degree": round(obj.lon, 2)  # Round to 2 decimal places
                    }
                except (KeyError, AttributeError):
                    logger.warning(f"Angle {angle} not found in chart")
                    continue
            
            # Calculate aspects with validation
            chart_aspects = []
            for planet1 in self.planets:
                for planet2 in self.planets:
                    if planet1 < planet2:  # Avoid duplicate aspects
                        try:
                            obj1 = chart.get(planet1)
                            obj2 = chart.get(planet2)
                            if obj1 and obj2:
                                aspect = flatlib_aspects.getAspect(obj1, obj2, const.MAJOR_ASPECTS)
                                if aspect:
                                    chart_aspects.append({
                                        "planet1": planet1,
                                        "planet2": planet2,
                                        "type": aspect.type,
                                        "orb": round(aspect.orb, 2)  # Round to 2 decimal places
                                    })
                        except KeyError:
                            continue
            
            chart_data = {
                "planets": planets,
                "houses": houses,
                "angles": angles,
                "aspects": chart_aspects,
                "calculation_date": date.isoformat(),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
            
            return {
                "status": "success",
                "data": chart_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating birth chart: {str(e)}")
            return {
                "status": "error",
                "error": f"Error calculating birth chart: {str(e)}"
            } 