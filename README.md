# Daily Heavens API

A FastAPI-based astrological birth chart calculation service that provides detailed planetary positions, aspects, and interpretations.

## Features

- Birth chart calculation using precise astronomical data
- Detailed planetary positions with signs and houses
- Aspect calculations between planets
- Support for retrograde motion detection
- House system calculations
- Angular point determinations (Ascendant, Midheaven, etc.)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dailyheavens.git
cd dailyheavens
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn app.main:app --reload --port 8080
```

2. Make a request to calculate a birth chart:
```bash
curl -X POST http://localhost:8080/api/v1/birthchart \
-H "Content-Type: application/json" \
-d '{
    "date_of_birth": "1990-01-01T12:00:00",
    "location": {
        "city": "San Francisco",
        "state": "California",
        "country": "United States",
        "timezone": "America/Los_Angeles",
        "latitude": 37.7749,
        "longitude": -122.4194
    }
}'
```

## API Documentation

### POST /api/v1/birthchart

Calculate a complete birth chart based on date, time, and location.

#### Request Body

- `date_of_birth`: ISO format datetime string
- `location`: Object containing:
  - `city`: String
  - `state`: String
  - `country`: String
  - `timezone`: IANA timezone string
  - `latitude`: Float
  - `longitude`: Float

#### Response

Returns a JSON object containing:
- Planetary positions (longitude, latitude, sign, house)
- Planetary motion (direct/retrograde)
- Aspects between planets
- House cusps
- Angular points (Asc, MC, Desc, IC)

## Project Structure

```
dailyheavens/
├── app/
│   ├── api/
│   │   └── birth_chart.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── birth_chart.py
│   ├── services/
│   │   └── birth_chart.py
│   └── main.py
├── data/
│   ├── planetary_qualities.json
│   ├── house_qualities.json
│   └── sign_qualities.json
├── requirements.txt
└── test_flatlib.py
```

## Dependencies

- FastAPI
- Uvicorn
- Flatlib (astronomical calculations)
- Pydantic
- Python-dateutil

## License

[License details]