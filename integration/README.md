# Daily Heavens Integration

This directory contains the integration layer between the backend services and the frontend application.

## Overview

The integration layer provides:

1. A unified API endpoint that follows the frontend's expected format
2. Translation between frontend requests and backend services
3. ZIP code to latitude/longitude conversion
4. Proper error handling and format adaptation

## Architecture

```
┌───────────┐     ┌───────────────┐     ┌─────────────────┐
│  Next.js  │ --> │    Adapter    │ --> │  Birth Chart    │
│ Frontend  │     │   Service     │     │    Service      │
└───────────┘     └───────────────┘     └─────────────────┘
                         │                      │
                         │                      V
                         │               ┌─────────────────┐
                         └─────────────>│ Interpretation  │
                                        │    Service      │
                                        └─────────────────┘
```

## API Endpoints

The adapter service exposes the following endpoints:

- `POST /birth-chart`: Calculate a birth chart based on frontend request format
- `GET /health`: Health check endpoint
- `GET /`: Root endpoint with service information

## Request Format

The frontend sends requests in this format:

```json
{
  "birth_date": "06/15/1990",
  "birth_time": "14:30",
  "birth_place_zip": "10001"
}
```

## Response Format

The adapter returns responses in this format:

```json
{
  "planets": {
    "sun": {
      "sign": "Gemini",
      "degrees": 24.5,
      "latitude": 0.0,
      "sign_longitude": 24.5,
      "speed": 0.95,
      "orb": 5.0,
      "mean_motion": 0.98,
      "movement": "Direct",
      "gender": "Masculine",
      "element": "Air",
      "is_fast": true,
      "house": 10
    },
    // ... other planets
  },
  "houses": {
    "house1": {
      "sign": "Virgo",
      "degrees": 10.5,
      "sign_longitude": 10.5,
      "condition": "Angular",
      "gender": "Feminine",
      "size": 30.0,
      "planets": []
    },
    // ... other houses
  },
  "angles": {
    "ascendant": {
      "sign": "Virgo",
      "degrees": 10.5,
      "sign_longitude": 10.5
    },
    // ... other angles
  },
  "aspects": [
    {
      "planet1": "sun",
      "planet2": "moon",
      "aspect": "trine",
      "orb": 2.3,
      "nature": "harmonious"
    },
    // ... other aspects
  ]
}
```

## Running Locally

To run the adapter service locally:

```bash
cd integration
pip install -r requirements.txt
uvicorn birth_chart_adapter:app --host 0.0.0.0 --port 8000
```

Or use the test script:

```bash
chmod +x test_integration.sh
./test_integration.sh
```

## Environment Variables

- `BIRTH_CHART_API_URL`: URL of the birth chart service (default: `http://localhost:8001/api/v1/birthchart`)
- `INTERPRETATION_API_URL`: URL of the interpretation service (default: `http://localhost:8002/api/v1/interpretation`)

## Deployment

This service can be deployed to Vercel as a Python serverless function. For local development, Docker Compose is recommended:

```bash
docker-compose up
``` 