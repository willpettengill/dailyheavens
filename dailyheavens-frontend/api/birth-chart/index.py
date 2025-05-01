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
    # Use June 20, 1988 04:15 EDT for testing the GET endpoint
    # Note: Location is still NYC for simplicity
    return {
        "date": "1988-06-20T04:15:00-04:00",  # Aware ISO string for the target date
        "latitude": 40.7128,                 # New York City latitude
        "longitude": -74.0060,               # New York City longitude
        # Timezone parameter is not strictly needed by the service now, 
        # but kept here for potential future use or clarity
        "timezone": "America/New_York"       
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
                # Pass the aware ISO string from test_data, remove timezone kwarg
                birth_chart = service.calculate_birth_chart(
                    date_of_birth=test_data["date"],
                    latitude=test_data["latitude"],
                    longitude=test_data["longitude"]
                    # timezone=test_data["timezone"] # Removed
                )
                logger.info("Successfully calculated birth chart")
                
                # Log key details about the calculated chart
                if birth_chart and birth_chart.get("status") == "success" and birth_chart.get("data"):
                    data = birth_chart["data"]
                    if "planets" in data and "Sun" in data["planets"]:
                        logger.info(f"GET - SUN SIGN: {data['planets']['Sun'].get('sign', 'Unknown')}")
                    if "calculation_date" in data:
                        logger.info(f"GET - CALCULATION DATE: {data['calculation_date']}")
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
            request_data = {}
            if content_length > 0:
                body = self.rfile.read(content_length)
                try:
                    request_data = json.loads(body.decode('utf-8'))
                    logger.info(f"Received POST data: {request_data}")
                except json.JSONDecodeError as json_err:
                    logger.error(f"Error decoding JSON body: {json_err}")
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid JSON format"}).encode('utf-8'))
                    return
            else:
                 logger.warning("Received POST request with no body or Content-Length=0")
                 # Fallback or error? For now, let's return an error as we expect data.
                 self.send_response(400)
                 self.send_header('Content-type', 'application/json')
                 self.end_headers()
                 self.wfile.write(json.dumps({"error": "Missing request body"}).encode('utf-8'))
                 return

            # Extract data using frontend keys, add checks
            birth_date_str = request_data.get("birth_date")
            birth_time_str = request_data.get("birth_time")
            zip_code = request_data.get("birth_place_zip")

            if not all([birth_date_str, birth_time_str, zip_code]):
                missing = [k for k, v in {"birth_date": birth_date_str, "birth_time": birth_time_str, "birth_place_zip": zip_code}.items() if not v]
                error_msg = f"Missing required fields: {', '.join(missing)}"
                logger.error(error_msg)
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": error_msg}).encode('utf-8'))
                return

            # Combine date and time for the service
            # For now, use placeholder/test values for lat/lon/tz while using the actual birth date/time
            test_geo = create_test_data() 
            
            # Create a timezone-aware ISO string including the offset (-04:00 for EDT)
            # TODO: Replace hardcoded offset with dynamic lookup based on date/zip
            offset_str = "-04:00" 
            date_of_birth_iso = f"{birth_date_str}T{birth_time_str}:00{offset_str}"
            
            logger.info(f"Calculating chart for: Date={birth_date_str}, Time={birth_time_str}, Zip={zip_code}")
            logger.info(f"Passing timezone-aware ISO string to service: {date_of_birth_iso}")

            # Calculate birth chart using correct argument names and user's actual birth date/time
            try:
                # Pass the ISO string; the service will parse it. Remove the timezone parameter.
                birth_chart = service.calculate_birth_chart(
                    date_of_birth=date_of_birth_iso,  
                    latitude=test_geo['latitude'],        
                    longitude=test_geo['longitude']
                    # timezone parameter removed
                )
                logger.info("Successfully calculated birth chart using user's birth date/time")
                
                # Log key details about the calculated chart
                if birth_chart and birth_chart.get("status") == "success" and birth_chart.get("data"):
                    data = birth_chart["data"]
                    logger.info(f"POST - FULL CHART RESULT: {json.dumps(data['planets'])}")
                    if "planets" in data and "Sun" in data["planets"]:
                        logger.info(f"POST - SUN SIGN: {data['planets']['Sun'].get('sign', 'Unknown')}")
                    if "calculation_date" in data:
                        logger.info(f"POST - CALCULATION DATE: {data['calculation_date']}")
            except Exception as calc_error:
                logger.error(f"Error calculating birth chart: {str(calc_error)}", exc_info=True)
                raise # Re-raise to trigger 500 error response
            
            # Prepare response
            response = {
                "message": "Birth chart calculation successful",
                "received_data": request_data,
                "birth_chart": birth_chart
            }
            
            # Log the full response structure (using list to make it JSON serializable)
            logger.info(f"POST - RESPONSE STRUCTURE: {list(response.keys())}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            logger.info("Sending successful response")
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error in POST handler: {str(e)}", exc_info=True)
            # Avoid sending response if headers already sent (e.g., in JSON decode error block)
            if not self.wfile.closed:
              try:
                  self.send_response(500)
                  self.send_header('Content-type', 'application/json')
                  self.end_headers()
                  self.wfile.write(json.dumps({
                      "error": str(e),
                      "message": "Failed to process birth chart request"
                  }).encode('utf-8'))
              except BrokenPipeError:
                  logger.warning("Client closed connection before error response could be sent.")
              except Exception as send_err:
                  logger.error(f"Failed to send error response: {send_err}")