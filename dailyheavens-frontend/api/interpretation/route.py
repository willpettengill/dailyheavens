from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
# Also add API directory for local data access
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# Import the interpretation service
from app.services.interpretation import InterpretationService

# Adjust file paths for serverless environment
os.environ['DATA_DIR'] = os.path.join(os.path.dirname(__file__), '../../data')
os.environ['TEMPLATES_DIR'] = os.path.join(os.path.dirname(__file__), '../../templates')

# Initialize the service
interpretation_service = InterpretationService()

# Set Jinja2 environment for templates in serverless environment
from jinja2 import Environment, FileSystemLoader
interpretation_service.jinja_env = Environment(
    loader=FileSystemLoader(os.environ['TEMPLATES_DIR']),
    trim_blocks=True,
    lstrip_blocks=True
)

# Vercel serverless function handler
def handler(req):
    """Serverless handler for birth chart interpretation."""
    try:
        # Parse request body
        content_length = int(req.headers.get('Content-Length', 0))
        body = json.loads(req.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}
        
        # Extract required parameters
        birth_chart = body.get('birth_chart')
        level = body.get('level', 'basic')
        area = body.get('area', 'general')
        
        # Validate inputs
        if not birth_chart:
            req.send_response(400)
            req.send_header('Content-Type', 'application/json')
            req.end_headers()
            response = {
                'status': 'error',
                'message': 'Missing required parameter: birth_chart'
            }
            req.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Generate interpretation
        interpretation = interpretation_service.generate_interpretation(
            birth_chart=birth_chart,
            level=level
        )
        
        # Return response
        req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        
        response = {
            'status': 'success',
            'data': {
                'birth_chart': birth_chart,
                'interpretations': interpretation
            }
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
            'message': f'Error generating interpretation: {str(e)}'
        }
        
        req.wfile.write(json.dumps(response).encode('utf-8'))
        return 