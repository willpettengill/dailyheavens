#!/bin/bash

# Set up error handling
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Daily Heavens API Integration Test${NC}"

# Start the API server
echo -e "${YELLOW}Starting API server...${NC}"
cd api
python -m uvicorn index:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Give server time to start
sleep 3

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
  echo -e "${GREEN}Health check passed${NC}"
else
  echo -e "${RED}Health check failed${NC}"
  kill $API_PID
  exit 1
fi

# Test birth chart endpoint with valid data
echo -e "${YELLOW}Testing birth chart endpoint...${NC}"
BIRTH_CHART_RESPONSE=$(curl -s -X POST http://localhost:8000/birth-chart \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "06/15/1988",
    "birth_time": "14:30",
    "latitude": 40.7128,
    "longitude": -74.0060
  }')

# Check if the response contains a success status
if [[ $BIRTH_CHART_RESPONSE == *"success"* || $BIRTH_CHART_RESPONSE == *"partial_success"* ]]; then
  echo -e "${GREEN}Birth chart test passed${NC}"
else
  echo -e "${RED}Birth chart test failed:${NC}"
  echo $BIRTH_CHART_RESPONSE
  kill $API_PID
  exit 1
fi

# Test with ZIP code
echo -e "${YELLOW}Testing with ZIP code...${NC}"
ZIP_RESPONSE=$(curl -s -X POST http://localhost:8000/birth-chart \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "06/15/1988",
    "birth_time": "14:30",
    "zip_code": "10001"
  }')

# Check if the response contains a success status
if [[ $ZIP_RESPONSE == *"success"* || $ZIP_RESPONSE == *"partial_success"* ]]; then
  echo -e "${GREEN}ZIP code test passed${NC}"
else
  echo -e "${RED}ZIP code test failed:${NC}"
  echo $ZIP_RESPONSE
  kill $API_PID
  exit 1
fi

# Test with invalid data
echo -e "${YELLOW}Testing with invalid data...${NC}"
INVALID_RESPONSE=$(curl -s -X POST http://localhost:8000/birth-chart \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "invalid-date",
    "birth_time": "14:30"
  }')

# Check if the response contains an error status
if [[ $INVALID_RESPONSE == *"error"* || $INVALID_RESPONSE == *"detail"* ]]; then
  echo -e "${GREEN}Invalid data test passed${NC}"
else
  echo -e "${RED}Invalid data test failed - expected error response${NC}"
  echo $INVALID_RESPONSE
  kill $API_PID
  exit 1
fi

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
kill $API_PID

echo -e "${GREEN}All tests passed!${NC}" 