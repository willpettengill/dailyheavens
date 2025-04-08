import json
from http.server import BaseHTTPRequestHandler

class VercelAdapter(BaseHTTPRequestHandler):
    """Adapter for Vercel serverless functions."""
    
    @staticmethod
    def adapt(handler_function):
        """
        Adapts a handler function to Vercel's serverless format.
        
        Args:
            handler_function: Function that takes (body, query_params) and returns response data
            
        Returns:
            A function compatible with Vercel's serverless format
        """
        def _adapted_handler(req):
            # Get request method
            method = req.method
            
            # Parse body if present
            body = {}
            if method in ['POST', 'PUT']:
                content_length = int(req.headers.get('Content-Length', 0))
                body = json.loads(req.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}
            
            # Parse query parameters
            query_params = {}
            if '?' in req.path:
                query_string = req.path.split('?', 1)[1]
                query_params = {k: v for k, v in [param.split('=') for param in query_string.split('&')]}
            
            # Call the handler function
            result = handler_function(body, query_params)
            
            # Set response headers
            req.send_response(result.get('statusCode', 200))
            req.send_header('Content-Type', 'application/json')
            req.end_headers()
            
            # Send response
            req.wfile.write(json.dumps(result.get('body', {})).encode('utf-8'))
            return
        
        return _adapted_handler 