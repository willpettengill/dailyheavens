from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
# Also add API directory for local data access
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# Import the birth chart service
from app.services.birth_chart import BirthChartService

# Adjust file paths for serverless environment
os.environ['DATA_DIR'] = os.path.join(os.path.dirname(__file__), '../../data')

# Initialize the service
birth_chart_service = BirthChartService()

# Vercel serverless function handler
def handler(req):
    """Serverless handler for birth chart calculation."""
    try:
        # Parse request body
        content_length = int(req.headers.get('Content-Length', 0))
        body = json.loads(req.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}
        
        # Extract required parameters
        date = body.get('date')
        latitude = body.get('latitude')
        longitude = body.get('longitude')
        timezone = body.get('timezone', 'UTC')
        
        # Validate inputs
        if not all([date, latitude, longitude]):
            req.send_response(400)
            req.send_header('Content-Type', 'application/json')
            req.end_headers()
            response = {
                'status': 'error',
                'message': 'Missing required parameters: date, latitude, longitude'
            }
            req.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Calculate birth chart
        chart_data = birth_chart_service.calculate_birth_chart(
            date_of_birth=date,
            latitude=latitude,
            longitude=longitude
        )
        
        # Return response
        req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        
        response = {
            'status': 'success',
            'data': chart_data
        }
        
        req.wfile.write(json.dumps(response, default=str).encode('utf-8'))
        return
        
    except Exception as e:
        # Return error response
        req.send_response(500)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        
        response = {
            'status': 'error',
            'message': f'Error calculating birth chart: {str(e)}'
        }
        
        req.wfile.write(json.dumps(response).encode('utf-8'))
        return 