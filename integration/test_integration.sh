#!/bin/bash

# Start the birth chart service
echo "Starting birth chart service..."
uvicorn app.birth_chart_server:app --host 0.0.0.0 --port 8001 &
BIRTH_CHART_PID=$!

# Wait for the birth chart service to start
sleep 3

# Start the interpretation service
echo "Starting interpretation service..."
uvicorn app.main:app --host 0.0.0.0 --port 8002 &
INTERPRETATION_PID=$!

# Wait for the interpretation service to start
sleep 3

# Start the adapter service
echo "Starting frontend adapter service..."
cd integration
uvicorn birth_chart_adapter:app --host 0.0.0.0 --port 8000 &
ADAPTER_PID=$!

# Wait for the adapter service to start
sleep 3

# Test the adapter service
echo "Testing adapter service..."
curl -X POST -H "Content-Type: application/json" -d '{
  "birth_date": "06/15/1990",
  "birth_time": "14:30",
  "birth_place_zip": "10001"
}' http://localhost:8000/birth-chart

# Wait for user input to stop the services
echo ""
echo "Press any key to stop the services..."
read -n 1

# Stop the services
echo "Stopping services..."
kill $BIRTH_CHART_PID
kill $INTERPRETATION_PID
kill $ADAPTER_PID

echo "Done!" 