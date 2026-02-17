"""
Options Chain API Endpoint

Returns real options chain data from Yahoo Finance.
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
            expiry = params.get("expiry", [None])[0]
            only_expiries = params.get("only_expiries", ["false"])[0].lower() == "true"

            if not ticker:
                self._send_response(400, {"error": "Missing required parameter: ticker"})
                return

            ticker = ticker.strip().upper()
            valid, _ = validate_ticker(ticker)
            if not valid:
                self._send_response(404, {"error": f"Invalid or unsupported ticker: {ticker}"})
                return

            fetcher = MarketDataFetcher(ticker)

            if only_expiries:
                self._send_response(200, {"expiries": fetcher.get_options_expiries()})
                return

            chain_data = fetcher.get_options_chain(expiry=expiry)
            chain_data["ticker"] = ticker
            chain_data["spot_price"] = round(fetcher.spot_price, 2)

            self._send_response(200, chain_data)

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, code, data):
        self.send_response(code)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

