from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects
from pprint import pprint

def explore_object(obj, chart):
    """Extract all relevant data from a flatlib object."""
    try:
        data = {
            "name": obj.id,
            "longitude": obj.lon,
            "latitude": obj.lat,
            "sign": obj.sign,
            "sign_longitude": obj.signlon,
            "movement": obj.movement() if hasattr(obj, 'movement') else "N/A",
            "element": obj.element() if hasattr(obj, 'element') else "N/A",
            "is_direct": obj.isDirect() if hasattr(obj, 'isDirect') else False,
            "is_retrograde": obj.isRetrograde() if hasattr(obj, 'isRetrograde') else False,
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
    except Exception as e:
        return {"error": str(e)}

def explore_available_objects(chart):
    """Try to explore all possible objects in flatlib to see what's available."""
    available_objects = {}
    
    # Try all constants from flatlib.const
    for name in dir(const):
        if name.isupper() and not name.startswith('_'):
            try:
                obj_id = getattr(const, name)
                if isinstance(obj_id, str):
                    try:
                        obj = chart.get(obj_id)
                        available_objects[name] = {
                            "id": obj_id,
                            "type": type(obj).__name__,
                            "sign": obj.sign if hasattr(obj, 'sign') else "N/A",
                            "lon": obj.lon if hasattr(obj, 'lon') else "N/A",
                        }
                    except:
                        pass
            except:
                pass
    
    return available_objects

def run_default_test():
    # Create chart for default test (San Francisco, Jan 1, 1990)
    date = Datetime('1990/01/01', '12:00')
    pos = GeoPos(37.7749, -122.4194)
    chart = Chart(date, pos)

    # Explore planets
    planets_data = {}
    for planet in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN,
                  const.URANUS, const.NEPTUNE, const.PLUTO, const.NORTH_NODE, const.SOUTH_NODE, const.CHIRON]:
        try:
            obj = chart.get(planet)
            planets_data[planet] = explore_object(obj, chart)
        except Exception as e:
            planets_data[planet] = {"error": str(e)}

    # Explore houses
    houses_data = {}
    for i in range(1, 13):
        try:
            house = chart.get(f"House{i}")
            houses_data[i] = {
                "longitude": house.lon,
                "sign": house.sign,
                "sign_longitude": house.signlon,
            }
        except Exception as e:
            houses_data[i] = {"error": str(e)}

    # Explore angles
    angles_data = {}
    for angle in [const.ASC, const.MC, const.DESC, const.IC]:
        try:
            obj = chart.get(angle)
            angles_data[angle] = {
                "longitude": obj.lon,
                "sign": obj.sign,
                "sign_longitude": obj.signlon,
            }
        except Exception as e:
            angles_data[angle] = {"error": str(e)}

    print("\nPLANETS:")
    pprint(planets_data)
    print("\nHOUSES:")
    pprint(houses_data)
    print("\nANGLES:")
    pprint(angles_data)

def run_will_test():
    # Create chart for Will's birth date (June 20, 1988, 4:15 AM, Sudbury, MA)
    print("\n\n*** TESTING WILL'S BIRTH CHART (1988/06/20, 4:15, Sudbury MA) ***")
    date = Datetime('1988/06/20', '04:15', '+0000')  # Using UTC
    pos = GeoPos(42.3834, -71.4161)  # Sudbury, MA coordinates
    chart = Chart(date, pos)

    # Explore all available objects
    print("\nAVAILABLE OBJECTS:")
    available = explore_available_objects(chart)
    pprint(available)

    # Explore planets specifically for the issue
    planets_data = {}
    for planet in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN,
                  const.URANUS, const.NEPTUNE, const.PLUTO, const.NORTH_NODE, const.SOUTH_NODE, const.CHIRON]:
        try:
            obj = chart.get(planet)
            planets_data[planet] = explore_object(obj, chart)
        except Exception as e:
            planets_data[planet] = {"error": str(e)}

    # Explore angles (focus on these since they're a problem)
    angles_data = {}
    for angle in [const.ASC, const.MC, const.DESC, const.IC]:
        try:
            obj = chart.get(angle)
            angles_data[angle] = {
                "longitude": obj.lon,
                "sign": obj.sign,
                "sign_longitude": obj.signlon,
            }
        except Exception as e:
            angles_data[angle] = {"error": str(e)}

    print("\nPLANETS FOR WILL:")
    pprint(planets_data)
    print("\nANGLES FOR WILL:")
    pprint(angles_data)

    # Specifically check for retrograde planets
    print("\nCHECKING RETROGRADE STATUS:")
    for planet in [const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]:
        try:
            obj = chart.get(planet)
            is_retro = obj.isRetrograde() if hasattr(obj, 'isRetrograde') else "unknown"
            movement = obj.movement() if hasattr(obj, 'movement') else "unknown"
            print(f"{planet}: Retrograde={is_retro}, Movement={movement}")
        except Exception as e:
            print(f"{planet}: Error={str(e)}")

    # Specifically check for north/south nodes and Chiron
    print("\nCHECKING NODES AND CHIRON:")
    for special in [const.NORTH_NODE, const.SOUTH_NODE, const.CHIRON]:
        try:
            obj = chart.get(special)
            print(f"{special}: Sign={obj.sign}, Lon={obj.lon}")
        except Exception as e:
            print(f"{special}: Error={str(e)}")

    # Try direct instantiation for special objects
    print("\nTRYING DIRECT INSTANTIATION:")
    try:
        from flatlib.object import Node, FixedStar
        north_node = Node(const.NORTH_NODE, chart.date, chart.pos)
        print(f"North Node direct: Sign={north_node.sign}, Lon={north_node.lon}")
    except Exception as e:
        print(f"Direct Node instantiation error: {str(e)}")

# Run tests
if __name__ == "__main__":
    print("*** RUNNING DEFAULT TEST ***")
    run_default_test()
    
    print("\n\n*** RUNNING WILL'S TEST ***")
    run_will_test() 