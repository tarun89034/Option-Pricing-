"""
Exchange Rate API Endpoint

Returns real-time exchange rates from Yahoo Finance.
"""

import json
import sys
import os
import yfinance as yf
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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

            source = params.get("source", ["USD"])[0].upper()
            target = params.get("target", ["USD"])[0].upper()

            if source == target:
                rate = 1.0
            else:
                def get_usd_rate(currency):
                    if currency == "USD": return 1.0
                    majors = ["EUR", "GBP"]
                    t = f"{currency}=X"
                    h = yf.Ticker(t).history(period="1d")
                    if not h.empty:
                        val = float(h["Close"].iloc[-1])
                        if currency in majors:
                            return val
                        else:
                            return 1.0 / val if val != 0 else 0
                    return None

                rate_s = get_usd_rate(source)
                rate_t = get_usd_rate(target)
                
                if rate_s is None or rate_t is None:
                    self._send_response(404, {"error": f"Could not determine exchange rate for {source}/{target}"})
                    return
                
                rate = rate_s / rate_t

            self._send_response(200, {
                "source": source,
                "target": target,
                "rate": rate,
                "timestamp": "latest"
            })

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, code, data):
        self.send_response(code)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

