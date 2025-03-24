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
cd ..

# Wait for all services to be ready
sleep 3

echo "All services are running:"
echo "- Birth Chart Service: http://localhost:8001"
echo "- Interpretation Service: http://localhost:8002"
echo "- Frontend Adapter: http://localhost:8000"
echo ""
echo "To test the adapter:"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{\"birth_date\": \"06/15/1990\", \"birth_time\": \"14:30\", \"birth_place_zip\": \"10001\"}' http://localhost:8000/birth-chart"
echo ""
echo "Press CTRL+C to stop all services..."

# Wait for CTRL+C
wait $BIRTH_CHART_PID

# Clean up
kill $BIRTH_CHART_PID
kill $INTERPRETATION_PID
kill $ADAPTER_PID

echo "All services stopped." 