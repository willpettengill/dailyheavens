# Daily Heavens API Documentation

## Overview
The Daily Heavens API consists of two independent services for birth chart calculation and astrological interpretation. Each service is designed to be simple to use while providing comprehensive astrological analysis.

## Services

### 1. Birth Chart Service (Port 8001)

Base URL: `http://localhost:8001/api/v1`

#### Calculate Birth Chart
Calculate a birth chart for a given date and location.

**Endpoint:** `POST /birthchart`

**Request Body:**
```json
{
    "date": "1990-01-01T12:00:00Z",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "planets": {
            "Sun": {
                "sign": "Capricorn",
                "degree": 10.5,
                "house": 1
            },
            "Moon": {
                "sign": "Aries",
                "degree": 15.2,
                "house": 4
            },
            "Mars": {
                "sign": "Leo",
                "degree": 22.8,
                "house": 8
            },
            "Ascendant": {
                "sign": "Capricorn",
                "degree": 5.0
            }
        },
        "houses": {
            "1": {
                "sign": "Capricorn",
                "degree": 5.0
            },
            "4": {
                "sign": "Aries",
                "degree": 15.0
            },
            "8": {
                "sign": "Leo",
                "degree": 22.0
            }
        },
        "angles": {
            "ASC": {
                "sign": "Capricorn",
                "degree": 5.0
            },
            "MC": {
                "sign": "Libra",
                "degree": 15.0
            }
        },
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "type": "conjunction",
                "orb": 4.7
            }
        ]
    }
}
```

### 2. Interpretation Service (Port 8002)

Base URL: `http://localhost:8002/api/v1`

#### Generate Interpretation
Generate an astrological interpretation for a birth chart.

**Endpoint:** `POST /interpretation`

**Request Body:**
```json
{
    "birth_chart": {
        "planets": {
            "Sun": {
                "sign": "Capricorn",
                "degree": 10.5,
                "house": 1
            },
            "Moon": {
                "sign": "Aries",
                "degree": 15.2,
                "house": 4
            }
        }
    },
    "level": "detailed",
    "area": "general"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "interpretations": {
            "planets": {
                "sun": "Sun in Capricorn represents leadership and vitality...",
                "moon": "Moon in Aries represents emotions and instincts..."
            },
            "houses": {
                "1": "House 1 in Capricorn represents self-expression and personality...",
                "4": "House 4 in Aries represents home and family..."
            },
            "aspects": {
                "sun-moon": "Sun conjunct Moon indicates a strong connection between conscious and unconscious..."
            }
        },
        "patterns": {
            "elements": {
                "fire": 1,
                "earth": 1,
                "air": 0,
                "water": 0
            },
            "modalities": {
                "cardinal": 2,
                "fixed": 0,
                "mutable": 0
            },
            "interpretation": "The chart shows a balance between fire and earth elements..."
        }
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "status": "error",
    "message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
}
```

### 422 Validation Error
```json
{
    "status": "error",
    "message": "Latitude must be between -90 and 90 degrees"
}
```

### 500 Internal Server Error
```json
{
    "status": "error",
    "message": "An unexpected error occurred"
}
```

## Best Practices
1. Always validate input data before sending requests
2. Cache responses when possible to minimize API calls
3. Use appropriate error handling for all API calls
4. Ensure timezone information is correctly specified
5. Keep birth chart data for reuse in interpretation requests

## Support
For API support and documentation:
- Documentation: http://localhost:8001/api/docs (Birth Chart Service)
- Documentation: http://localhost:8002/api/docs (Interpretation Service) 