from http.server import BaseHTTPRequestHandler
import json
import logging
import sys
from pathlib import Path
from .birth_chart import BirthChartService

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create test data for birth chart calculation."""
    return {
        "date": "2024-03-19T12:00:00Z",  # Noon UTC on March 19, 2024
        "latitude": 40.7128,              # New York City latitude
        "longitude": -74.0060,            # New York City longitude
        "timezone": "America/New_York"    # NYC timezone
    }

class handler(BaseHTTPRequestHandler):
    def initialize_service(self):
        """Initialize BirthChartService with proper error handling."""
        try:
            # Log data directory location
            data_dir = Path(__file__).parent.parent / "data"
            logger.info(f"Data directory path: {data_dir}")
            logger.info(f"Data directory exists: {data_dir.exists()}")
            
            if data_dir.exists():
                structured_dir = data_dir / "structured"
                logger.info(f"Structured data directory exists: {structured_dir.exists()}")
                if structured_dir.exists():
                    files = list(structured_dir.glob("*.json"))
                    logger.info(f"Found JSON files in structured directory: {[f.name for f in files]}")
            
            logger.info("Initializing BirthChartService...")
            service = BirthChartService()
            logger.info("Successfully initialized BirthChartService")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize BirthChartService: {str(e)}")
            raise

    def do_GET(self):
        try:
            # Initialize service with detailed logging
            service = self.initialize_service()
            
            # Use test data
            test_data = create_test_data()
            logger.info(f"Using test data: {test_data}")
            
            # Calculate birth chart
            try:
                birth_chart = service.calculate_birth_chart(
                    date_of_birth=test_data["date"],
                    latitude=test_data["latitude"],
                    longitude=test_data["longitude"],
                    timezone=test_data["timezone"]
                )
                logger.info("Successfully calculated birth chart")
            except Exception as calc_error:
                logger.error(f"Error calculating birth chart: {str(calc_error)}")
                raise
            
            # Prepare response
            response = {
                "message": "Birth chart calculation successful",
                "test_data": test_data,
                "birth_chart": birth_chart
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            logger.info("Sending successful response")
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in birth chart handler: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "message": "Failed to calculate birth chart"
            }).encode('utf-8'))
    
    def do_POST(self):
        try:
            # Initialize service with detailed logging
            service = self.initialize_service()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                request_data = json.loads(body.decode('utf-8'))
            else:
                # If no body provided, use test data
                request_data = create_test_data()
            
            # Calculate birth chart
            try:
                birth_chart = service.calculate_birth_chart(
                    date_of_birth=request_data.get("date", create_test_data()["date"]),
                    latitude=request_data.get("latitude", create_test_data()["latitude"]),
                    longitude=request_data.get("longitude", create_test_data()["longitude"]),
                    timezone=request_data.get("timezone", create_test_data()["timezone"])
                )
                logger.info("Successfully calculated birth chart")
            except Exception as calc_error:
                logger.error(f"Error calculating birth chart: {str(calc_error)}")
                raise
            
            # Prepare response
            response = {
                "message": "Birth chart calculation successful",
                "request_data": request_data,
                "birth_chart": birth_chart
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            logger.info("Sending successful response")
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in birth chart handler: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "message": "Failed to calculate birth chart"
            }).encode('utf-8'))