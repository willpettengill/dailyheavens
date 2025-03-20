import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, List
import pytz
import sys

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects

from app.core.config import settings

logger = logging.getLogger(__name__)

class BirthChartService:
    """Service for calculating and analyzing birth charts."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent
        else:
            self.data_dir = Path(data_dir)
            
        # Define the list of planets we want to calculate
        self.planets = [
            const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
            const.JUPITER, const.SATURN
        ]
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        self.planets_data = {}
        self.houses_data = {}
        self.signs_data = {}
        self.aspects_data = {}
        self.dignities_data = {}
        
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
        try:
            for i in range(1, 13):
                try:
                    house = chart.get(f"House{i}")
                    next_house = chart.get(f"House{(i % 12) + 1}")
                    if house and next_house:
                        if (house.lon <= longitude < next_house.lon) or \
                           (house.lon > next_house.lon and (longitude >= house.lon or longitude < next_house.lon)):
                            return i
                except Exception as e:
                    self.logger.debug(f"Error getting house {i}: {str(e)}")
                    continue
            return 1  # Default to first house if not found
        except Exception as e:
            self.logger.error(f"Error calculating house number: {str(e)}")
            return 1  # Default to first house on error

    def _get_planet_data(self, obj: Any, chart: Chart) -> Dict[str, Any]:
        """Extract all available data for a planet."""
        try:
            house_num = self._get_house_number(chart, obj.lon)
            
            # Get aspects with other planets
            planet_aspects = []
            for other_planet in self.planets:
                if other_planet != obj.id:
                    try:
                        other_obj = chart.get(other_planet)
                        if other_obj:
                            aspect = aspects.getAspect(obj, other_obj, const.MAJOR_ASPECTS)
                            if aspect:
                                planet_aspects.append({
                                    "planet": other_planet,
                                    "type": aspect.type,
                                    "orb": aspect.orb,
                                    "qualities": self.aspects_data.get(aspect.type, {})
                                })
                    except Exception as e:
                        self.logger.debug(f"Error getting aspect between {obj.id} and {other_planet}: {str(e)}")
                        continue
            
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
        except Exception as e:
            self.logger.error(f"Error extracting planet data for {obj.id}: {str(e)}")
            raise

    def _create_chart(self, date_str: str, time_str: str, lat: float, lon: float, utc_offset: int) -> Chart:
        """Create a flatlib Chart object."""
        try:
            # Create flatlib objects
            date = Datetime(date_str, time_str, utc_offset)
            pos = GeoPos(lat, lon)
            
            # Log the values for debugging
            self.logger.debug(f"Created GeoPos object: {pos}")
            self.logger.debug(f"Created Datetime object: {date}")
            self.logger.debug(f"Raw values - Date: {date_str}, Time: {time_str}, Lat: {lat}, Lon: {lon}, UTC offset: {utc_offset}")
            self.logger.debug(f"Creating chart with date={date_str}, time={time_str}, lat={lat}, lon={lon}, utc_offset={utc_offset}")
            
            # Create chart without specifying planets
            chart = Chart(date, pos)
            return chart
        except Exception as e:
            self.logger.error(f"Error creating chart: {str(e)}")
            raise

    def calculate_birth_chart(self, date_of_birth: str, latitude: float, longitude: float, timezone: str = "UTC") -> Dict[str, Any]:
        """Calculate a birth chart for the given date and location."""
        try:
            # Parse the date string to get date, time, and UTC offset
            dt = datetime.fromisoformat(date_of_birth)
            tz = pytz.timezone(timezone)
            dt = dt.astimezone(tz)
            
            # Format date and time for flatlib
            date_str = dt.strftime("%Y/%m/%d")
            time_str = dt.strftime("%H:%M")
            utc_offset = int(dt.utcoffset().total_seconds() / 3600)
            
            self.logger.debug(f"Creating flatlib datetime with: date={date_str}, time={time_str}, utc_offset={utc_offset}")
            
            # Create chart
            chart = self._create_chart(date_str, time_str, latitude, longitude, utc_offset)
            
            # Extract data from chart
            planets_data = {}
            for planet in self.planets:
                try:
                    obj = chart.get(planet)
                    if obj:
                        planets_data[planet] = self._get_planet_data(obj, chart)
                except Exception as e:
                    self.logger.warning(f"Error getting planet {planet}: {str(e)}")
                    continue
            
            # Extract house data
            houses_data = {}
            for i in range(1, 13):
                try:
                    house = chart.get(f"House{i}")
                    if house:
                        houses_data[i] = {
                            "longitude": house.lon,
                            "sign": house.sign,
                            "sign_longitude": house.signlon,
                        }
                except Exception as e:
                    self.logger.warning(f"Error getting house {i}: {str(e)}")
                    continue
            
            # Extract angle data
            angles_data = {}
            for angle in [const.ASC, const.MC, const.DESC, const.IC]:
                try:
                    obj = chart.get(angle)
                    if obj:
                        angles_data[angle] = {
                            "longitude": obj.lon,
                            "sign": obj.sign,
                            "sign_longitude": obj.signlon,
                        }
                except Exception as e:
                    self.logger.warning(f"Error getting angle {angle}: {str(e)}")
                    continue
            
            # Validate the data
            if not self._validate_chart_data(chart, planets_data, houses_data, angles_data):
                return {
                    "status": "error",
                    "error": "Invalid chart data"
                }
            
            return {
                "status": "success",
                "data": {
                    "planets": planets_data,
                    "houses": houses_data,
                    "angles": angles_data
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating birth chart: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _validate_chart_data(self, chart: Chart, planets: Dict[str, Any], houses: Dict[str, Any], angles: Dict[str, Any]) -> bool:
        """Validate that all required data is present in the chart."""
        try:
            logger.debug(f"Validating chart data - Houses: {list(houses.keys())}, Planets: {list(planets.keys())}, Angles: {list(angles.keys())}")
            
            # Required planets (excluding outer planets)
            required_planets = [
                const.SUN, const.MOON, const.MERCURY, const.VENUS, 
                const.MARS, const.JUPITER, const.SATURN
            ]
            
            # Validate required planets
            for planet in required_planets:
                if planet not in planets:
                    logger.error(f"Required planet {planet} not found in calculated data")
                    return False
            
            # Optional planets (outer planets)
            optional_planets = [const.URANUS, const.NEPTUNE, const.PLUTO]
            for planet in optional_planets:
                if planet not in planets:
                    logger.warning(f"Optional planet {planet} not found in calculated data")
            
            # Validate houses
            required_houses = 10  # We require at least 10 houses
            if len(houses) < required_houses:
                logger.error(f"Insufficient houses calculated: {len(houses)}/{required_houses}")
                return False
            
            # Validate angles
            required_angles = [const.ASC, const.MC]
            for angle in required_angles:
                if angle not in angles:
                    logger.error(f"Required angle {angle} not found in calculated data")
                    return False
            
            logger.debug("Chart data validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating chart data: {str(e)}")
            return False 