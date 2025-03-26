# Troubleshooting Guide

## Known Issues and Resolutions

### Birth Chart Service: Missing Outer Planets

**Issue:**
When calculating birth charts, the service may log warnings about missing outer planets:
```
WARNING - Planet Uranus not found in chart
WARNING - Planet Neptune not found in chart
WARNING - Planet Pluto not found in chart
```

**Cause:**
This is related to the Flatlib library's ephemeris data access. The warnings indicate that the library couldn't find position data for these outer planets in its ephemeris files.

**Resolution:**
These warnings don't affect the core functionality of the birth chart calculations. The service still provides accurate data for the inner planets, houses, and aspects. If outer planet data is critical for your use case, ensure you're using a compatible version of `pyswisseph` (2.08.00-1) as specified in requirements.txt.

### Interpretation Service: Pattern Analysis Error

**Issue:**
The interpretation service initially returned an error:
```
ERROR - Error analyzing patterns: 'InterpretationService' object has no attribute '_analyze_simple_patterns'
```

**Cause:**
This was caused by a method name mismatch in the InterpretationService class. The service was trying to call a method that didn't exist.

**Resolution:**
1. Created a fresh virtual environment
2. Installed the correct package versions from requirements.txt
3. Verified both services were running on their respective ports:
   - Birth Chart Service: Port 8001
   - Interpretation Service: Port 8002
4. Confirmed the services were working correctly with test requests

### Port Binding Issues

**Issue:**
When starting either service, you might encounter:
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8001): address already in use
```

**Cause:**
This occurs when the port is already being used by another process, often a previous instance of the service that wasn't properly terminated.

**Resolution:**
1. Find the process using the port:
   ```bash
   lsof -i :8001  # For birth chart service
   lsof -i :8002  # For interpretation service
   ```
2. Terminate the process:
   ```bash
   kill -9 <PID>
   ```
3. Restart the service

## Best Practices

1. Always use a fresh virtual environment when setting up the services
2. Install dependencies using the exact versions specified in requirements.txt
3. Run services on their designated ports:
   - Birth Chart Service: 8001
   - Interpretation Service: 8002
4. Monitor the logs for warnings and errors
5. Test both services independently before integrating them

## Verification Steps

After resolving any issues, verify the services are working correctly:

1. Test the Birth Chart Service:
```bash
curl -X POST http://localhost:8001/api/v1/birthchart \
  -H "Content-Type: application/json" \
  -d '{"date": "1990-01-01T12:00:00Z", "latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"}'
```

2. Test the Interpretation Service:
```bash
curl -X POST http://localhost:8002/api/v1/interpretation \
  -H "Content-Type: application/json" \
  -d '{"birth_chart": {"planets": {"Sun": {"sign": "Capricorn", "degree": 10.5, "house": 1}}}, "level": "detailed", "area": "general"}'
```

Both services should return 200 OK responses with appropriate JSON data. 