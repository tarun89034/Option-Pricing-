"""
Market Data API Endpoint

Returns stock info and historical price data for a given ticker.
"""

import json
import sys
import os
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.market_data_fetcher import MarketDataFetcher, validate_ticker


from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def _handle_request(self):
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            ticker = params.get("ticker", [None])[0]
            period = params.get("period", ["1y"])[0]

            if not ticker:
                self._send_response(400, {"error": "Missing required parameter: ticker"})
                return

            ticker = ticker.strip().upper()
            valid, _ = validate_ticker(ticker)
            if not valid:
                self._send_response(404, {"error": f"Invalid or unsupported ticker: {ticker}"})
                return

            fetcher = MarketDataFetcher(ticker)
            stock_info = fetcher.get_stock_info()
            historical = fetcher.get_historical_data(period=period)

            result = {
                "stock_info": stock_info,
                "historical_data": historical,
                "period": period,
            }

            self._send_response(200, result)

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, code, data):
        self.send_response(code)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

