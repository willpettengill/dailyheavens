# Daily Heavens API Documentation

## Overview
The Daily Heavens API provides endpoints for calculating birth charts and generating astrological interpretations. The API is designed to be simple to use while providing comprehensive astrological analysis.

## Base URL
```
https://api.dailyheavens.com/v1
```

## Authentication
All API requests require an API key to be included in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Calculate Birth Chart
Calculate a birth chart for a given date and location.

**Endpoint:** `POST /birth-chart`

**Request Body:**
```json
{
    "date_of_birth": "1990-01-01T12:00:00Z",
    "latitude": 40.7128,
    "longitude": -74.0060
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
        ],
        "calculation_date": "2024-03-20T12:00:00Z",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
}
```

### 2. Generate Interpretation
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
    "area": "relationships"
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
            }
        },
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "type": "conjunction",
                "orb": 4.7
            }
        ],
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
            },
            "combinations": {
                "sun_moon": "Sun in Capricorn with Moon in Aries suggests a personality that blends ambition with emotional independence...",
                "sun_rising": "Sun in Capricorn with Capricorn Ascending suggests a focused and determined personality...",
                "moon_rising": "Moon in Aries with Capricorn Ascending suggests emotional needs expressed through a practical personality..."
            }
        },
        "patterns": {
            "counts": {
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
                }
            },
            "dominant": {
                "elements": ["fire", "earth"],
                "modalities": ["cardinal"]
            },
            "interpretation": "The chart shows a balance between fire and earth elements..."
        },
        "combinations": {
            "sun_moon": {
                "interpretation": "Sun in Capricorn with Moon in Aries suggests...",
                "strength": 0.5
            }
        },
        "house_emphasis": {
            "counts": {
                "angular": 2,
                "succedent": 0,
                "cadent": 0
            },
            "dominant": "angular",
            "interpretation": "Emphasis on angular houses indicates a focus on action and initiative..."
        },
        "special_configurations": {
            "configurations": {
                "grand_trine": [],
                "t_square": [],
                "grand_cross": [],
                "yod": [],
                "stellium": []
            },
            "interpretation": "No major configurations found."
        },
        "planetary_dignities": {
            "sun": "neutral",
            "moon": "neutral"
        }
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "status": "error",
    "message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
}
```

### 401 Unauthorized
```json
{
    "status": "error",
    "message": "Invalid or missing API key"
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

## Rate Limiting
- Free tier: 100 requests per day
- Pro tier: 1000 requests per day
- Enterprise tier: Custom limits

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616239020
```

## Best Practices
1. Always validate input data before sending requests
2. Cache responses when possible to minimize API calls
3. Handle rate limiting gracefully
4. Use appropriate error handling for all API calls
5. Keep API keys secure and never expose them in client-side code

## Support
For API support, please contact:
- Email: support@dailyheavens.com
- Documentation: https://docs.dailyheavens.com
- Status page: https://status.dailyheavens.com 