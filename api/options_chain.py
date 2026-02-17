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


CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def handler(request):
    """Handle options chain requests."""
    if hasattr(request, "method") and request.method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        # Parse query parameters
        if hasattr(request, "url"):
            parsed = urlparse(request.url)
            params = parse_qs(parsed.query)
        elif hasattr(request, "args"):
            params = {k: [v] for k, v in request.args.items()}
        else:
            params = {}

        ticker = params.get("ticker", [None])[0]
        expiry = params.get("expiry", [None])[0]

        only_expiries = params.get("only_expiries", ["false"])[0].lower() == "true"

        if not ticker:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing required parameter: ticker"}),
            }

        ticker = ticker.strip().upper()
        valid, _ = validate_ticker(ticker)
        if not valid:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Invalid or unsupported ticker: {ticker}"}),
            }

        fetcher = MarketDataFetcher(ticker)

        if only_expiries:
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"expiries": fetcher.get_options_expiries()}),
            }

        chain_data = fetcher.get_options_chain(expiry=expiry)
        chain_data["ticker"] = ticker
        chain_data["spot_price"] = round(fetcher.spot_price, 2)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(chain_data),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
