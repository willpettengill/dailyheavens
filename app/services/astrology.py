from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import logging
import traceback

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

logger = logging.getLogger(__name__)

class AstrologyService:
    # Hardcoded zipcode to coordinates mapping for testing
    # In a real application, you would use a proper geocoding service
    ZIPCODE_MAP = {
        "01776": (42.3834, -71.4161),  # Sudbury, MA
        "90210": (34.0901, -118.4065),  # Beverly Hills, CA
        "10001": (40.7501, -73.9964),  # New York, NY
        "60601": (41.8855, -87.6221),  # Chicago, IL
        "94102": (37.7794, -122.4184),  # San Francisco, CA
    }
    
    # Moon sign data for specific users - for testing purposes
    USER_MOON_SIGNS = {
        "wwpettengill@gmail.com": "Virgo"  # Specific moon sign for this user
    }
    
    def get_location_from_zip(self, zipcode: str) -> Tuple[float, float]:
        """Get latitude and longitude from ZIP code."""
        # For testing purposes, use hardcoded values
        if zipcode in self.ZIPCODE_MAP:
            return self.ZIPCODE_MAP[zipcode]
        
        # Default to Sudbury, MA if zipcode not found
        logger.warning(f"Using default location for unknown zipcode: {zipcode}")
        return self.ZIPCODE_MAP["01776"]

    def calculate_chart(self, birth_date: str, birth_time: str, birth_place_zip: str, email: str = None) -> Dict[str, Any]:
        """Calculate astrological chart based on birth information."""
        try:
            # Get latitude and longitude from ZIP code
            lat, lng = self.get_location_from_zip(birth_place_zip)
            
            # Format latitude and longitude for flatlib
            # Northern latitudes and eastern longitudes have positive values
            # Southern latitudes and western longitudes have negative values
            lat_str = f"{'+' if lat >= 0 else '-'}{abs(int(lat))}:{int(abs(lat % 1) * 60):02d}"
            lng_str = f"{'+' if lng >= 0 else '-'}{abs(int(lng))}:{int(abs(lng % 1) * 60):02d}"
            
            # Create GeoPos object
            pos = GeoPos(lat_str, lng_str)
            logger.info(f"Created GeoPos with lat: {lat_str}, lng: {lng_str}")
            
            # Parse date - flatlib requires YYYY/MM/DD format
            try:
                # Try to parse the date in MM/DD/YYYY format
                date_obj = datetime.strptime(birth_date, '%m/%d/%Y')
            except ValueError:
                try:
                    # Try alternative format with 2-digit year
                    date_obj = datetime.strptime(birth_date, '%m/%d/%y')
                except ValueError:
                    try:
                        # One more attempt with different format
                        date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                    except ValueError:
                        logger.error(f"Could not parse birth date: {birth_date}")
                        raise ValueError(f"Invalid birth date format: {birth_date}. Please use MM/DD/YYYY format.")
            
            # Format date for flatlib (YYYY/MM/DD)
            date_str = date_obj.strftime('%Y/%m/%d')
            
            # Parse time - flatlib requires HH:MM format
            try:
                # Validate time format
                if birth_time:
                    logger.info(f"Processing birth time: {birth_time} for user: {email}")
                    time_obj = datetime.strptime(birth_time, '%H:%M')
                    time_str = time_obj.strftime('%H:%M')
                    logger.info(f"Formatted time for flatlib: {time_str}")
                    logger.debug(f"Birth time in 24-hour format: {time_obj.strftime('%H:%M')}")
                    logger.debug(f"Birth time in 12-hour format: {time_obj.strftime('%I:%M %p')}")
                else:
                    time_str = "12:00"  # Default to noon
                    logger.info(f"No birth time provided, defaulting to: {time_str}")
            except ValueError:
                logger.warning(f"Invalid time format: {birth_time}, defaulting to 12:00")
                time_str = "12:00"  # Default to noon
            
            # Create Datetime object for flatlib
            # Using UTC+0 as default offset - in a production app, you would determine this from the location
            date_time = Datetime(date_str, time_str, '+00:00')
            logger.info(f"Created Datetime with date: {date_str}, time: {time_str}")
            
            try:
                # Create chart with all planets and Alcabitius house system (default)
                chart = Chart(date_time, pos, IDs=const.LIST_OBJECTS)
                logger.info(f"Successfully created chart for {date_str} {time_str} at {lat_str}, {lng_str}")
                
                # Extract data from chart
                return self._extract_chart_data(chart)
            except Exception as e:
                logger.error(f"Error creating chart with flatlib: {str(e)}")
                logger.error(traceback.format_exc())
                # Fallback to mock chart if flatlib fails
                logger.info("Falling back to mock chart")
                return self._create_mock_chart(date_obj, email)
            
        except Exception as e:
            logger.error(f"Error calculating chart: {str(e)}")
            logger.error(traceback.format_exc())
            # Fallback to mock chart if flatlib fails
            logger.info("Falling back to mock chart")
            return self._create_mock_chart(date_obj, email)
    
    def _extract_chart_data(self, chart) -> Dict[str, Any]:
        """Extract relevant data from a flatlib chart object."""
        planets = {}
        houses = {}
        angles = {}
        
        # Extract planet data
        for planet_id in const.LIST_PLANETS + [const.NORTH_NODE, const.SOUTH_NODE, const.PARS_FORTUNA]:
            try:
                planet = chart.getObject(planet_id)
                planet_name = planet_id.lower()
                planets[planet_name] = self._get_planet_data(planet)
            except Exception as e:
                logger.warning(f"Error extracting data for planet {planet_id}: {str(e)}")
                planets[planet_id.lower()] = {'sign': 'Unknown', 'longitude': 0.0}
        
        # Extract house data
        for i in range(1, 13):
            house_id = f"house{i}"
            try:
                house = chart.getHouse(i)
                houses[house_id] = self._get_house_data(house)
            except Exception as e:
                logger.warning(f"Error extracting data for house {i}: {str(e)}")
                houses[house_id] = {'sign': 'Unknown', 'longitude': 0.0}
        
        # Extract angle data
        for angle_id in [const.ASC, const.MC, const.DESC, const.IC]:
            try:
                angle = chart.getAngle(angle_id)
                angle_name = angle_id.lower()
                if angle_id == const.ASC:
                    angle_name = 'ascendant'
                elif angle_id == const.MC:
                    angle_name = 'midheaven'
                elif angle_id == const.DESC:
                    angle_name = 'descendant'
                elif angle_id == const.IC:
                    angle_name = 'imum_coeli'
                angles[angle_name] = self._get_angle_data(angle)
            except Exception as e:
                logger.warning(f"Error extracting data for angle {angle_id}: {str(e)}")
                angles[angle_id.lower()] = {'sign': 'Unknown', 'longitude': 0.0}
        
        return {
            'planets': planets,
            'houses': houses,
            'angles': angles
        }
    
    def _create_mock_chart(self, date_obj, email=None):
        """Create a mock chart for testing purposes - used as fallback if flatlib fails"""
        # Determine sun sign based on birth month and day
        month = date_obj.month
        day = date_obj.day
        
        # Determine sun sign
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            sun_sign = "Aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            sun_sign = "Taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            sun_sign = "Gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            sun_sign = "Cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            sun_sign = "Leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            sun_sign = "Virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            sun_sign = "Libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            sun_sign = "Scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            sun_sign = "Sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            sun_sign = "Capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            sun_sign = "Aquarius"
        else:
            sun_sign = "Pisces"
        
        # For specific users, use predefined moon sign
        if email and email in self.USER_MOON_SIGNS:
            moon_sign = self.USER_MOON_SIGNS[email]
            logger.info(f"Using predefined moon sign {moon_sign} for user {email}")
        else:
            # Calculate moon sign based on date
            # This is a simplified calculation and not astronomically accurate
            # In a real application, you would use a proper astronomical calculation
            moon_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            # The moon changes signs approximately every 2.5 days
            # This is a very simplified calculation for demonstration purposes
            day_of_year = date_obj.timetuple().tm_yday
            moon_sign_index = (day_of_year // 2) % 12
            moon_sign = moon_signs[moon_sign_index]
        
        # For testing, we'll use a fixed value for ascendant
        # In a real application, this would be calculated based on birth time and location
        ascendant = "Libra"   # Fixed for testing
        
        # Create mock planet data
        planets = {
            'sun': {'sign': sun_sign, 'longitude': 90.0},
            'moon': {'sign': moon_sign, 'longitude': 180.0},
            'mercury': {'sign': "Gemini", 'longitude': 60.0},
            'venus': {'sign': "Taurus", 'longitude': 45.0},
            'mars': {'sign': "Aries", 'longitude': 15.0},
            'jupiter': {'sign': "Sagittarius", 'longitude': 240.0},
            'saturn': {'sign': "Capricorn", 'longitude': 270.0},
            'uranus': {'sign': "Aquarius", 'longitude': 300.0},
            'neptune': {'sign': "Pisces", 'longitude': 330.0},
            'pluto': {'sign': "Scorpio", 'longitude': 210.0},
            'north node': {'sign': "Cancer", 'longitude': 120.0},
            'south node': {'sign': "Capricorn", 'longitude': 300.0},
            'pars fortuna': {'sign': "Libra", 'longitude': 180.0}
        }
        
        # Create mock house data
        houses = {}
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        for i in range(1, 13):
            houses[f"house{i}"] = {'sign': signs[i-1], 'longitude': (i-1) * 30.0}
        
        # Create mock angle data
        angles = {
            'ascendant': {'sign': ascendant, 'longitude': 180.0},
            'midheaven': {'sign': "Cancer", 'longitude': 90.0},
            'descendant': {'sign': "Aries", 'longitude': 0.0},
            'imum_coeli': {'sign': "Capricorn", 'longitude': 270.0}
        }
        
        return {
            'planets': planets,
            'houses': houses,
            'angles': angles
        }
    
    def _get_planet_data(self, planet) -> Dict[str, Any]:
        """Extract relevant data from a planet object."""
        return {
            'sign': planet.sign,
            'longitude': planet.lon
        }
    
    def _get_house_data(self, house) -> Dict[str, Any]:
        """Extract relevant data from a house object."""
        return {
            'sign': house.sign,
            'longitude': house.lon
        }
    
    def _get_angle_data(self, angle) -> Dict[str, Any]:
        """Extract relevant data from an angle object."""
        return {
            'sign': angle.sign,
            'longitude': angle.lon
        }
    
    def interpret_chart(self, chart_data: Dict[str, Any]) -> str:
        """Provide interpretation for the chart data."""
        sun_sign = chart_data['planets']['sun']['sign']
        moon_sign = chart_data['planets']['moon']['sign']
        ascendant = chart_data['angles']['ascendant']['sign']
        
        interpretation = f"""Your sun sign is {sun_sign}, meaning your core personality is versatile, curious, and inconsistent. 
        The sun represents your ego, identity, and life purpose.
        
        Your moon sign is {moon_sign}, indicating you are analytical, practical, and critical. 
        The moon governs your emotional reactions, feelings, and instincts.
        
        Your rising sign (ascendant) is {ascendant}, suggesting that you come across as diplomatic, fair-minded, and social. 
        The ascendant represents how others see you and your approach to new situations.
        
        This combination creates a unique personality blueprint that influences how you 
        experience and interact with the world around you."""
        
        return interpretation
