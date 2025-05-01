"""Serverless Function Handler for Astrological Interpretations."""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
# import markdown2 # No longer needed as handler returns JSON
from typing import Dict, Optional, Tuple

# --- Configuration --- #
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = logging.DEBUG

# --- Set up logging --- #
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)
logger.info(f"Logger initialized with level: {logging.getLevelName(logger.level)}")

# --- Interpretation Service Initialization --- #
interpretation_service = None
service_initialization_error = None
try:
    logger.info("Attempting to import and initialize InterpretationService...")
    from .interpretation import InterpretationService
    interpretation_service = InterpretationService(logger_instance=logger)
    logger.info("InterpretationService imported and initialized successfully.")
except ImportError as e:
    service_initialization_error = f"Failed to import InterpretationService: {e}"
    logger.error(service_initialization_error, exc_info=True)
except FileNotFoundError as e:
    service_initialization_error = f"Failed to initialize InterpretationService (missing data/template files?): {e}"
    logger.error(service_initialization_error, exc_info=True)
except Exception as e:
    service_initialization_error = f"Unexpected error initializing InterpretationService: {e}"
    logger.error(service_initialization_error, exc_info=True)

# --- Test Data for GET Requests --- #
# Using the June 20, 1988 example from previous context
# Note: Aspects might be simplified/example data
TEST_BIRTH_CHART_DATA = {
  "date": "1988-06-20T04:15:00-04:00",
  "location": "New York, USA",
  "coords": "40.7128,-74.0060",
  "tz_str": "America/New_York",
  "planets": {
    "Sun": {"sign": "Gemini", "degree": 29.25, "house": 1, "speed": 0.96, "retrograde": False},
    "Moon": {"sign": "Virgo", "degree": 15.80, "house": 4, "speed": 13.50, "retrograde": False},
    "Mercury": {"sign": "Cancer", "degree": 5.50, "house": 1, "speed": 1.20, "retrograde": False},
    "Venus": {"sign": "Leo", "degree": 10.10, "house": 2, "speed": 1.15, "retrograde": False},
    "Mars": {"sign": "Aries", "degree": 22.30, "house": 11, "speed": 0.70, "retrograde": False},
    "Jupiter": {"sign": "Taurus", "degree": 28.90, "house": 12, "speed": 0.10, "retrograde": True},
    "Saturn": {"sign": "Capricorn", "degree": 0.50, "house": 7, "speed": -0.05, "retrograde": True},
    "Uranus": {"sign": "Sagittarius", "degree": 29.80, "house": 7, "speed": -0.03, "retrograde": True},
    "Neptune": {"sign": "Capricorn", "degree": 9.20, "house": 7, "speed": -0.01, "retrograde": True},
    "Pluto": {"sign": "Scorpio", "degree": 10.60, "house": 5, "speed": -0.02, "retrograde": True}
    # Add other points if needed by interpretation logic (Nodes, Chiron etc)
  },
  "houses": {
    "1": {"sign": "Gemini", "degree": 18.5},
    "2": {"sign": "Cancer", "degree": 12.0},
    "3": {"sign": "Leo", "degree": 9.0},
    "4": {"sign": "Virgo", "degree": 11.0},
    "5": {"sign": "Libra", "degree": 15.0},
    "6": {"sign": "Scorpio", "degree": 18.0},
    "7": {"sign": "Sagittarius", "degree": 18.5},
    "8": {"sign": "Capricorn", "degree": 12.0},
    "9": {"sign": "Aquarius", "degree": 9.0},
    "10": {"sign": "Pisces", "degree": 11.0},
    "11": {"sign": "Aries", "degree": 15.0},
    "12": {"sign": "Taurus", "degree": 18.0}
  },
  "angles": {
      "ascendant": {"sign": "Gemini", "degree": 18.5},
      "midheaven": {"sign": "Pisces", "degree": 11.0},
      "descendant": {"sign": "Sagittarius", "degree": 18.5},
      "imum_coeli": {"sign": "Virgo", "degree": 11.0}
  },
  "aspects": [
      # Example aspects - replace with actual calculated aspects if needed
      {"planet1": "Sun", "planet2": "Moon", "type": 90, "orb": 2.5},
      {"planet1": "Sun", "planet2": "Mars", "type": 120, "orb": 1.8},
      {"planet1": "Moon", "planet2": "Saturn", "type": 120, "orb": 3.1},
      {"planet1": "Mercury", "planet2": "Neptune", "type": 60, "orb": 0.5}
  ]
}

# --- HTTP Request Handler --- #
class handler(BaseHTTPRequestHandler):
    """Handles requests to the /api/interpretation endpoint."""

    def _check_service(self) -> bool:
        """Checks if the interpretation service is available and sends error if not."""
        if not interpretation_service:
            error_message = f"Interpretation service is unavailable. Initialization error: {service_initialization_error or 'Unknown'}"
            self._send_json_response({"success": False, "error": error_message}, 500)
            logger.critical("InterpretationService is unavailable. Cannot process request.")
            return False
        return True

    def _send_json_response(self, data: Dict, status_code: int = 200):
        """Sends a JSON response with appropriate headers."""
        try:
            json_output = json.dumps(data)
            encoded_output = json_output.encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded_output)))
            self.end_headers()
            self.wfile.write(encoded_output)
            logger.info(f"Successfully sent JSON response (Status: {status_code}, Size: {len(encoded_output)} bytes).")
        except Exception as e:
             logger.error(f"Error sending JSON response: {e}", exc_info=True)
             # If headers not sent, try sending an error
             if not self.headers_sent:
                 # Use a simpler error response if JSON serialization failed
                 fallback_error = json.dumps({"success": False, "error": "Failed to serialize or send JSON response."}).encode('utf-8')
                 self.send_response(500)
                 self.send_header('Content-type', 'application/json; charset=utf-8')
                 self.send_header('Content-Length', str(len(fallback_error)))
                 self.end_headers()
                 self.wfile.write(fallback_error)

    def _process_interpretation_request(self, birth_chart: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Generates interpretation JSON. Returns (json_result, error_message)."""
        logger.info("Calling InterpretationService to generate interpretation...")
        interpretation_result = interpretation_service.generate_interpretation(
            birth_chart=birth_chart,
            level="basic" # Using basic level for now
        )

        if not interpretation_result or not interpretation_result.get("success"):
            error_msg = interpretation_result.get("error", "Unknown error during interpretation generation")
            logger.error(f"Interpretation generation failed: {error_msg}")
            return None, f"Failed to generate interpretation: {error_msg}"

        logger.info("Interpretation generated successfully.")
        logger.debug(f"Interpretation result keys: {list(interpretation_result.keys())}")
        # No HTML rendering here, return the raw result dictionary
        return interpretation_result, None

    # --- Request Handling Methods --- #

    def do_POST(self):
        """Handles POST requests, expects JSON birth chart data."""
        logger.info("Received POST request to /api/interpretation")
        if not self._check_service():
            return

        try:
            # --- Get Request Body --- #
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Request body is empty")
                logger.warning("Received POST request with empty body.")
                return

            post_body = self.rfile.read(content_length)
            logger.debug(f"Received raw POST body (first 100 chars): {post_body[:100]}...")

            # --- Parse JSON Data --- #
            try:
                birth_chart_data = json.loads(post_body)
                logger.info("Successfully parsed JSON request body.")
                logger.debug(f"Parsed birth chart data keys: {list(birth_chart_data.keys())}")
            except json.JSONDecodeError as e:
                self.send_error(400, f"Invalid JSON format: {e}")
                logger.error(f"Failed to parse JSON request body: {e}", exc_info=True)
                return
            except Exception as e:
                self.send_error(400, f"Error processing JSON data: {e}")
                logger.error(f"Unexpected error processing JSON: {e}", exc_info=True)
                return

            # --- Generate Interpretation & Get JSON Result --- #
            json_result, error_message = self._process_interpretation_request(birth_chart_data)

            # --- Send Response --- #
            if error_message:
                # Send error as JSON
                self._send_json_response({"success": False, "error": error_message}, 500)
            elif json_result:
                # Send successful interpretation as JSON
                self._send_json_response(json_result, 200)
            else:
                # Should not happen, but handle defensively
                 err_msg = "Failed to get interpretation result for unknown reason."
                 self._send_json_response({"success": False, "error": err_msg}, 500)
                 logger.error("Process function returned None for JSON without error message.")

        except Exception as e:
            # Generic error handler for unexpected issues during POST processing
            error_msg = f"Internal server error during POST: {e}"
            self._send_json_response({"success": False, "error": error_msg}, 500)
            logger.error(f"Unhandled exception during POST request processing: {e}", exc_info=True)

    def do_GET(self):
        """Handles GET requests. Renders interpretation using TEST_BIRTH_CHART_DATA."""
        logger.info("Received GET request to /api/interpretation")
        if not self._check_service():
            return

        try:
            logger.info("Processing GET request using test birth chart data.")
            json_result, error_message = self._process_interpretation_request(TEST_BIRTH_CHART_DATA)

            if error_message:
                self._send_json_response({"success": False, "error": error_message}, 500)
            elif json_result:
                self._send_json_response(json_result, 200)
            else:
                 err_msg = "Failed to generate interpretation JSON from test data."
                 self._send_json_response({"success": False, "error": err_msg}, 500)
                 logger.error("Process function returned None for JSON without error message (GET request).")

        except Exception as e:
            # Generic error handler for unexpected issues during GET processing
            error_msg = f"Internal server error during GET: {e}"
            self._send_json_response({"success": False, "error": error_msg}, 500)
            logger.error(f"Unhandled exception during GET request processing: {e}", exc_info=True)

# --- Vercel Entrypoint --- #
# The class `handler` inheriting from BaseHTTPRequestHandler is the Vercel entrypoint.

# Example usage (if run directly, not applicable in Vercel)
# if __name__ == '__main__':
#     from http.server import HTTPServer
#     server_address = ('', 8000)
#     httpd = HTTPServer(server_address, handler)
#     print(f"Server listening on port {server_address[1]}...")
#     httpd.serve_forever() 