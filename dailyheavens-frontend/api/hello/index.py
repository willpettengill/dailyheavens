from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import logging
import sys

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_sample_data():
    return pd.DataFrame({
        'planets': ['Mercury', 'Venus', 'Earth', 'Mars'],
        'type': ['Terrestrial'] * 4
    })

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = create_sample_data()
            response = {
                "message": "Hello from Python!",
                "total_planets": len(df),
                "planet_types": df['type'].value_counts().to_dict()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            logger.info(f"Returning response: {response}")
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in handler: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))