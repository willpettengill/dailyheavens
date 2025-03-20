# Troubleshooting Guide

This guide covers common issues you might encounter when running the Daily Heavens API and their solutions.

## Running the Server

### Prerequisites
1. Python 3.8 or higher
2. Virtual environment (venv)
3. All dependencies installed from `requirements.txt`

### Step-by-Step Server Setup

1. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Unix/macOS:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --log-level debug
   ```

### API Endpoints
- API documentation: `http://localhost:8000/api/docs`
- Birth chart endpoint: `http://localhost:8000/api/v1/birthchart`
- Interpretation endpoint: `http://localhost:8000/api/v1/interpretation`

## Common Issues and Solutions

### 1. Address Already in Use Error
**Error**: `ERROR: [Errno 48] Address already in use`

**Solutions**:
- Kill existing uvicorn processes:
  ```bash
  pkill -f uvicorn
  ```
- Or use a different port:
  ```bash
  uvicorn app.main:app --reload --port 8001 --log-level debug
  ```

### 2. Missing Required Planets Error
**Error**: `{"status":"error","data":{},"error":"Missing required planets: Ascendant"}`

**Solutions**:
- Check that the birth chart service includes the Ascendant in its calculations
- Verify that the flatlib library is properly installed and configured
- Ensure the birth data (date, time, location) is accurate and complete

### 3. Module Not Found Errors
**Error**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
- Ensure you're in the project root directory when running the server
- Check that your virtual environment is activated
- Verify that all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```

### 4. Data Directory Not Found
**Error**: `Structured data directory not found` or `File not found` warnings

**Solutions**:
- Verify that the `data/structured` directory exists and contains the required JSON files:
  - planets.json
  - houses.json
  - signs.json
  - aspects.json
  - dignities.json
- Check file permissions
- Ensure paths are correct for your operating system

### 5. Virtual Environment Issues
**Problem**: Multiple virtual environments activated or environment conflicts

**Solutions**:
- Deactivate all environments:
  ```bash
  # Run multiple times if needed
  deactivate
  # For conda environments
  conda deactivate
  ```
- Start fresh with project's venv:
  ```bash
  source venv/bin/activate
  ```

### 6. Invalid Birth Data Errors
**Error**: `Invalid date format` or coordinate range errors

**Solutions**:
- Use ISO format for dates: `YYYY-MM-DDTHH:MM:SS`
- Ensure latitude is between -90 and 90 degrees
- Ensure longitude is between -180 and 180 degrees
- Example valid request:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/birthchart" \
       -H "Content-Type: application/json" \
       -d '{"date": "1990-01-01T12:00:00Z", 
            "latitude": 40.7128, 
            "longitude": -74.0060, 
            "timezone": "America/New_York"}'
  ```

## Debugging Tips

1. **Check Server Logs**:
   - Run server with debug logging: `--log-level debug`
   - Check `logs/` directory for detailed logs

2. **Verify Data Files**:
   - All required JSON files should be in `data/structured/`
   - Files should be properly formatted JSON
   - Check file permissions

3. **Test Environment**:
   - Verify Python version: `python --version`
   - List installed packages: `pip freeze`
   - Compare with requirements.txt

4. **API Testing**:
   - Use the Swagger UI at `/api/docs` for interactive testing
   - Check response headers and status codes
   - Validate request payload format

## Getting Help

If you encounter issues not covered in this guide:
1. Check the GitHub issues
2. Review the API documentation
3. Ensure you're using the latest version
4. Include relevant logs and error messages when seeking help

## Chart Creation Issues

### Outer Planets Not Found in Chart

**Error Message:**
```
WARNING - Planet Uranus not found in chart
WARNING - Planet Neptune not found in chart
WARNING - Planet Pluto not found in chart
```

**Problem:**
The flatlib library does not support the outer planets (Uranus, Neptune, Pluto) in its default configuration. When these planets are included in the `IDs` parameter of the `Chart` constructor, the chart creation fails to find these planets, which can cause cascading failures in house calculations and other chart features.

**Solution:**
Remove the outer planets from the planet list in the `BirthChartService` class. The supported planets are:
- Sun
- Moon
- Mercury
- Venus
- Mars
- Jupiter
- Saturn

**Example Fix:**
```python
self.planets = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN
]
```

**Note:** If outer planet calculations are needed, consider using a different astrological library that supports these planets, or implement custom calculations for them.

### Timezone Handling Issues

**Error Message:**
```
WARNING - House 1 not found in chart
WARNING - House 2 not found in chart
...
```

**Problem:**
When creating a `Datetime` object for the chart, the UTC offset must be passed to the constructor. If the offset is not provided, the chart will be created with incorrect timezone information, leading to incorrect house calculations and other time-dependent features.

**Solution:**
Ensure the UTC offset is passed to the `Datetime` constructor when creating the chart:

```python
# Correct way
date = Datetime(date_str, time_str, utc_offset)

# Incorrect way (missing utc_offset)
date = Datetime(date_str, time_str)
```

**Note:** The UTC offset should be calculated from the timezone information:
```python
utc_offset = int(dt.utcoffset().total_seconds() / 3600)
``` 