#!/usr/bin/env python3
"""
Base handler with common functionality
"""

import http.server
import json
from urllib.parse import urlparse, parse_qs
from ..core.config import WORKSHOP_DIR


class BaseHandler(http.server.SimpleHTTPRequestHandler):
    """Base handler with common HTTP utilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSHOP_DIR, **kwargs)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        response = json.dumps(data, default=str, indent=2)
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {
            "success": False,
            "error": message
        }
        self.send_json_response(error_data, status_code)
    
    def get_post_data(self):
        """Get and parse POST data"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        return json.loads(post_data)
    
    def get_query_params(self):
        """Get query parameters from URL"""
        parsed_path = urlparse(self.path)
        return parse_qs(parsed_path.query)
    
    def end_headers(self):
        """Add no-cache headers for HTML files"""
        if hasattr(self, 'path') and self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()