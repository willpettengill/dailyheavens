# Flatlib Usage Guide

## House Access
When working with houses in flatlib, always use the following format:
```python
# Correct way to access houses
house = chart.get(f"House{i}")  # where i is the house number (1-12)

# Incorrect ways (do not use):
house = chart.getHouse(i)  # This will not work
house = chart.houses[i]    # This will not work
```

## Important Notes
1. House numbers are accessed using string format "House1", "House2", etc.
2. The `get()` method is the correct way to access house data
3. Each house object has the following attributes:
   - `sign`: The zodiac sign
   - `lon`: The longitude/degree
   - `size`: The size of the house in degrees

## Common Pitfalls
1. Using `getHouse()` method instead of `get("HouseX")`
2. Trying to access houses as array indices
3. Not handling the case where houses cross the 0° Aries point

## Example Usage
```python
# Create chart
chart = Chart(date, pos)

# Access house cusps
houses = {}
for i in range(1, 13):
    house = chart.get(f"House{i}")
    if house:
        houses[str(i)] = {
            "sign": house.sign,
            "degree": round(house.lon, 2),
            "size": round(house.size, 2)
        }
``` 