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

logger = logging.getLogger(__name__)

# Define the list of planets we want to calculate
PLANETS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]

class BirthChartService:
    """Service for calculating and analyzing birth charts."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Update to use the api/data directory
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.planets = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
            "Chiron" # Add Chiron to the list of planets
        ]
        self._load_structured_data()

    def _load_structured_data(self):
        """Load structured data from JSON files."""
        try:
            structured_dir = self.data_dir / "structured"
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
            if house and self._is_longitude_in_house(longitude, house.lon, chart.get(f"House{i%12+1}").lon):
                return i
        return None

    def _is_longitude_in_house(self, longitude, house_lon, next_house_lon):
        """Helper function to determine if a longitude is in a given house."""
        # Handle the special case where houses cross the 0/360 degree point
        if house_lon > next_house_lon:
            return longitude >= house_lon or longitude < next_house_lon
        # Normal case
        return house_lon <= longitude < next_house_lon

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
        """Calculate a birth chart for the given date and location, expecting a timezone-aware ISO string."""
        try:
            # Parse the timezone-aware ISO string directly
            dt = datetime.fromisoformat(date_of_birth)
            logger.info(f"Parsed aware datetime: {dt.isoformat()} (Timestamp: {dt.timestamp()})")
            
            # Format date and time for flatlib
            date_str = dt.strftime("%Y/%m/%d")
            time_str = dt.strftime("%H:%M")
            
            # Convert timezone to offset for flatlib using the parsed datetime
            tz_offset = dt.utcoffset()
            if tz_offset:
                hours = int(tz_offset.total_seconds() / 3600)
                minutes = int((tz_offset.total_seconds() % 3600) / 60)
                tz_str = f"{hours:+03d}{minutes:02d}"
            else:
                # This case might occur if the input string was unexpectedly naive, or UTC with no offset info
                tz_str = "+0000"
                logger.warning(f"Could not determine timezone offset from input string '{date_of_birth}'. Using +0000.")
            
            logger.info(f"Using flatlib datetime: Date={date_str}, Time={time_str}, TZ={tz_str}")

            # Create the GeoPos object *before* the test loop
            pos = GeoPos(float(latitude), float(longitude))
            
            # --- Start Flatlib Datetime Format Testing ---
            logger.info("--- Testing Flatlib Datetime Formats ---")
            test_formats_results = {}
            
            # Extract components from the aware datetime object (dt)
            t_year = dt.year
            t_month = dt.month
            t_day = dt.day
            t_hour = dt.hour
            t_minute = dt.minute
            t_second = dt.second
            t_offset_sign = '+' if tz_offset.total_seconds() >= 0 else '-'
            t_offset_hours = abs(int(tz_offset.total_seconds() / 3600))
            t_offset_minutes = abs(int((tz_offset.total_seconds() % 3600) / 60))
            
            # Derived strings/lists for testing
            t_date_str = f"{t_year}/{t_month:02d}/{t_day:02d}"
            t_time_str = f"{t_hour:02d}:{t_minute:02d}" # Flatlib expects HH:MM
            t_tz_str_no_colon = f"{t_offset_sign}{t_offset_hours:02d}{t_offset_minutes:02d}" # e.g., -0400
            t_tz_str_colon = f"{t_offset_sign}{t_offset_hours:02d}:{t_offset_minutes:02d}" # e.g., -04:00
            t_date_list = [t_year, t_month, t_day]
            # Time list format based on docs example ['+', 17, 0, 0] - sign seems to relate to time itself? Unclear. Let's try offset sign.
            t_time_list_signed = [t_offset_sign, t_hour, t_minute, t_second]
            t_time_list_unsigned = [t_hour, t_minute, t_second] # Maybe it ignores sign?

            # Convert dt to UTC for UTC test
            dt_utc = dt.astimezone(pytz.utc)
            t_utc_date_str = dt_utc.strftime("%Y/%m/%d")
            t_utc_time_str = dt_utc.strftime("%H:%M")
            t_utc_tz_str = "+0000"

            # Test Cases Definition
            test_cases = {
                "1_Current": lambda: Datetime(t_date_str, t_time_str, t_tz_str_no_colon), # Current method tz=-0400
                "2_TZ_Colon": lambda: Datetime(t_date_str, t_time_str, t_tz_str_colon),   # tz=-04:00
                "3_No_TZ": lambda: Datetime(t_date_str, t_time_str),                    # No tz string
                "4_List_DateOnly": lambda: Datetime(t_date_list),                       # List [Y,M,D]
                # "5_List_DateTime": lambda: Datetime(t_date_list, t_time_list_unsigned), # List [Y,M,D], [H,M,S] - Seems less likely based on docs
                "6_List_DateTimeSigned": lambda: Datetime(t_date_list, t_time_list_signed), # List [Y,M,D], ['-',H,M,S]
                "7_UTC_Components": lambda: Datetime(t_utc_date_str, t_utc_time_str, t_utc_tz_str) # Pass UTC components
            }

            # Run Test Cases
            for name, constructor in test_cases.items():
                try:
                    logger.info(f"Testing format '{name}'")
                    test_date = constructor()
                    test_chart = Chart(test_date, pos) # Use the same GeoPos
                    test_sun = test_chart.get(const.SUN)
                    if test_sun:
                        test_formats_results[name] = {"status": "success", "sun_sign": test_sun.sign, "sun_lon": test_sun.lon}
                        logger.info(f"Result format '{name}': Sun={test_sun.sign} ({test_sun.lon:.2f})")
                    else:
                        test_formats_results[name] = {"status": "error", "message": "Could not get Sun object"}
                        logger.warning(f"Result format '{name}': Could not get Sun object")
                except Exception as test_err:
                    test_formats_results[name] = {"status": "error", "message": str(test_err)}
                    logger.error(f"Error format '{name}': {test_err}")
            
            logger.info("--- Finished Testing Flatlib Datetime Formats ---")
            # --- End Flatlib Datetime Format Testing ---
            
            # Create flatlib objects using the *original* intended method for the actual result
            date = Datetime(date_str, time_str, tz_str)
            # Log Flatlib Datetime internal representation (Julian Day Universal Time)
            try:
                logger.info(f"Flatlib Datetime Object: date.jd={date.jd}, date.ut={date.ut}")
            except AttributeError:
                logger.warning("Could not log flatlib date.jd or date.ut")
                
            chart = Chart(date, pos)
            # Log Chart's interpretation of the date
            try:
                logger.info(f"Flatlib Chart Object Date: chart.date.jd={chart.date.jd}, chart.date.ut={chart.date.ut}")
            except AttributeError:
                 logger.warning("Could not log chart.date.jd or chart.date.ut")
                 
            # Log raw Sun longitude before extracting sign
            try:
                sun_obj = chart.get(const.SUN)
                if sun_obj:
                    logger.info(f"Flatlib Sun Object: lon={sun_obj.lon}, signlon={sun_obj.signlon}, sign={sun_obj.sign}")
                else:
                    logger.warning("Could not get Sun object from chart")
            except Exception as sun_err:
                logger.error(f"Error logging Sun object details: {sun_err}")

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
                        # Get retrograde status
                        is_retrograde = obj.isRetrograde() if hasattr(obj, 'isRetrograde') else False
                        # Get movement information
                        movement = obj.movement() if hasattr(obj, 'movement') else "Direct"
                        
                        planets[planet] = {
                            "sign": obj.sign,
                            "degree": round(obj.lon, 2),  # Round to 2 decimal places
                            "house": house_num,
                            "retrograde": is_retrograde,
                            "movement": movement
                        }
                except KeyError:
                    logger.warning(f"Planet {planet} not found in chart")
                    continue
            
            # Extract angles and map them correctly
            angles = {}
            angle_mappings = {
                "ASC": "ascendant",
                "MC": "midheaven",
                "DESC": "descendant",
                "IC": "imum_coeli"
            }
            
            for flatlib_name, output_name in angle_mappings.items():
                try:
                    angle_const = getattr(const, flatlib_name)
                    obj = chart.get(angle_const)
                    if obj:
                        angles[output_name] = {
                            "sign": obj.sign,
                            "degrees": round(obj.lon, 2)
                        }
                except (KeyError, AttributeError) as e:
                    logger.warning(f"Angle {flatlib_name} not found in chart: {str(e)}")
                    continue
            
            # Try to get north and south nodes
            special_points = {
                "NORTH_NODE": "north_node",
                "SOUTH_NODE": "south_node"
            }
            
            for flatlib_name, output_name in special_points.items():
                try:
                    if hasattr(const, flatlib_name):
                        point_const = getattr(const, flatlib_name)
                        obj = chart.get(point_const)
                        if obj:
                            house_num = self._get_house_number(chart, obj.lon)
                            planets[output_name] = {
                                "sign": obj.sign,
                                "degree": round(obj.lon, 2),
                                "house": house_num,
                                "retrograde": False,  # Nodes don't have retrograde motion
                                "movement": "Direct"
                            }
                except (KeyError, AttributeError) as e:
                    logger.debug(f"Special point {flatlib_name} not found in chart: {str(e)}")
                    continue
            
            # Validate minimum required planets
            required_planets = ["Sun", "Moon"]
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
                                    # Map aspect types to string values
                                    aspect_type_map = {
                                        0: "conjunction",
                                        60: "sextile",
                                        90: "square",
                                        120: "trine",
                                        180: "opposition"
                                    }
                                    aspect_type = aspect_type_map.get(aspect.type, str(aspect.type))
                                    
                                    chart_aspects.append({
                                        "planet1": planet1,
                                        "planet2": planet2,
                                        "type": aspect_type,
                                        "orb": round(aspect.orb, 2),  # Round to 2 decimal places
                                        "nature": "neutral"  # Default value
                                    })
                        except KeyError:
                            continue
            
            chart_data = {
                "planets": planets,
                "houses": houses,
                "angles": angles,
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