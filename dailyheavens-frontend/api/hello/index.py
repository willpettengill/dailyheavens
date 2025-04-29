from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import logging
import sys
import importlib.util
import os

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Test imports
try:
    import flatlib
    logger.info("Successfully imported flatlib")
    
    # Import BirthChartService using relative path
    birth_chart_path = os.path.join(os.path.dirname(__file__), '..', 'birth-chart', 'birth_chart.py')
    spec = importlib.util.spec_from_file_location("birth_chart", birth_chart_path)
    birth_chart_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(birth_chart_module)
    BirthChartService = birth_chart_module.BirthChartService
    logger.info("Successfully imported BirthChartService")
    
    IMPORTS_WORKING = True
except Exception as e:
    logger.error(f"Import error: {str(e)}")
    IMPORTS_WORKING = False

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
                "planet_types": df['type'].value_counts().to_dict(),
                "imports_working": IMPORTS_WORKING
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