"""
API Index -- Health check and endpoint listing.
"""

import json


from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "status": "ok",
            "service": "Option Pricing API",
            "endpoints": [
                {"path": "/api", "method": "GET", "description": "Health check and endpoint listing"},
                {"path": "/api/market_data", "method": "GET", "description": "Stock info and historical price data", "params": "ticker (required), period (optional, default: 1y)"},
                {"path": "/api/price_option", "method": "GET", "description": "Price an option using multiple models", "params": "ticker (required), option_type (call/put, default: call), strike (optional, ATM if omitted), days_to_expiry (required)"},
                {"path": "/api/options_chain", "method": "GET", "description": "Get real options chain data", "params": "ticker (required), expiry (optional)"},
            ],
        })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

