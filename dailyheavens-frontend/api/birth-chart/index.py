from http.server import BaseHTTPRequestHandler
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from urllib.parse import parse_qs, urlparse

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def parse_json_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length > 0:
        body = handler.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))
    return None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            request_data = parse_json_body(self)
            if not request_data:
                raise ValueError("Request body is required")

            logger.info(f"Birth chart calculation requested for date: {request_data.get('date')}")
            
            # Validate required fields
            required_fields = ['date', 'latitude', 'longitude']
            for field in required_fields:
                if field not in request_data:
                    raise ValueError(f"Missing required field: {field}")

            # Create test data
            test_data = pd.DataFrame({
                'planet': ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars'],
                'sign': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo'],
                'degree': np.random.randint(0, 30, 5),
                'timestamp': datetime.now().isoformat()
            })
            
            response = {
                "message": "Birth chart endpoint is working",
                "request": request_data,
                "test_data": test_data.to_dict(orient='records')
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in birth-chart handler: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "message": "Failed to calculate birth chart"
            }).encode('utf-8'))

    def do_GET(self):
        try:
            response = {
                "message": "Birth chart API is running",
                "endpoints": {
                    "POST /api/birth-chart": "Calculate birth chart"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in birth-chart handler: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode('utf-8'))