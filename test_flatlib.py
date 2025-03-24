from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects
from pprint import pprint

def explore_object(obj, chart):
    """Extract all relevant data from a flatlib object."""
    data = {
        "name": obj.id,
        "longitude": obj.lon,
        "latitude": obj.lat,
        "sign": obj.sign,
        "sign_longitude": obj.signlon,
        "movement": obj.movement,
        "element": obj.element(),
        "is_direct": obj.isDirect(),
        "is_retrograde": obj.isRetrograde(),
    }
    
    # Get aspects with other planets
    data["aspects"] = []
    for other_planet in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]:
        if other_planet != obj.id:
            other_obj = chart.get(other_planet)
            aspect = aspects.getAspect(obj, other_obj, const.MAJOR_ASPECTS)
            if aspect:
                data["aspects"].append({
                    "planet": other_planet,
                    "type": aspect.type,
                    "orb": aspect.orb,
                })
    
    return data

# Create chart
date = Datetime('1990/01/01', '12:00')
pos = GeoPos(37.7749, -122.4194)
chart = Chart(date, pos)

# Explore planets
planets_data = {}
for planet in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]:
    obj = chart.get(planet)
    planets_data[planet] = explore_object(obj, chart)

# Explore houses
houses_data = {}
for i in range(1, 13):
    house = chart.get(f"House{i}")
    houses_data[i] = {
        "longitude": house.lon,
        "sign": house.sign,
        "sign_longitude": house.signlon,
    }

# Explore angles
angles_data = {}
for angle in [const.ASC, const.MC, const.DESC, const.IC]:
    obj = chart.get(angle)
    angles_data[angle] = {
        "longitude": obj.lon,
        "sign": obj.sign,
        "sign_longitude": obj.signlon,
    }

print("\nPLANETS:")
pprint(planets_data)
print("\nHOUSES:")
pprint(houses_data)
print("\nANGLES:")
pprint(angles_data) 