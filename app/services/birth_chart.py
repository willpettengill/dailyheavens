import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any
import pytz

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

    def calculate_birth_chart(self, date_of_birth: str, latitude: float, longitude: float, timezone: str = "UTC") -> Dict[str, Any]:
        """Calculate a birth chart for the given date and location."""
        try:
            # Parse the input date as UTC
            dt = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            
            # Convert to the specified timezone
            if timezone != "UTC":
                tz = pytz.timezone(timezone)
                dt = dt.astimezone(tz)
            
            # Format date and time for flatlib
            date_str = dt.strftime("%Y/%m/%d")
            time_str = dt.strftime("%H:%M")
            
            # Convert timezone to offset for flatlib
            tz_offset = dt.utcoffset()
            if tz_offset:
                hours = int(tz_offset.total_seconds() / 3600)
                minutes = int((tz_offset.total_seconds() % 3600) / 60)
                tz_str = f"{hours:+03d}{minutes:02d}"
            else:
                tz_str = "+0000"
            
            # Create flatlib objects
            pos = GeoPos(float(latitude), float(longitude))
            date = Datetime(date_str, time_str, tz_str)
            chart = Chart(date, pos)
            
            # Extract house cusps
            houses = {}
            for i in range(1, 13):
                try:
                    house = chart.get(f"House{i}")
                    if house:
                        houses[str(i)] = {
                            "sign": house.sign,
                            "degree": round(house.lon, 2),
                            "size": round(house.size, 2)
                        }
                except (KeyError, AttributeError) as e:
                    logger.warning(f"Error calculating house {i}: {str(e)}")
                    continue
            
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
            
            # Extract angles with validation
            for angle in ["ASC", "MC"]:
                try:
                    obj = chart.get(getattr(const, angle))
                    if obj:
                        house_num = 1 if angle == "ASC" else 10  # ASC is house 1, MC is house 10
                        planets[angle] = {
                            "sign": obj.sign,
                            "degree": round(obj.lon, 2),  # Round to 2 decimal places
                            "house": house_num,
                            "retrograde": False  # Angles don't have retrograde motion
                        }
                except (KeyError, AttributeError):
                    logger.warning(f"Angle {angle} not found in chart")
                    continue
            
            # Map ASC to Ascendant in the output
            if "ASC" in planets:
                planets["Ascendant"] = planets.pop("ASC")
            if "MC" in planets:
                planets["Midheaven"] = planets.pop("MC")
            
            # Validate minimum required planets
            required_planets = ["Sun", "Moon", "Ascendant"]
            missing_planets = [p for p in required_planets if p not in planets]
            if missing_planets:
                return {
                    "status": "error",
                    "error": f"Missing required planets: {', '.join(missing_planets)}"
                }
            
            # Validate minimum required houses
            if len(houses) < 10:  # Allow some flexibility but require most houses
                return {
                    "status": "error",
                    "error": "Insufficient house data calculated"
                }
            
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
                "angles": {},
                "aspects": chart_aspects,
                "calculation_date": dt.isoformat(),
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