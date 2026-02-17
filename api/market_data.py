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


CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def handler(request):
    """Handle market data requests."""
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
        period = params.get("period", ["1y"])[0]

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
        stock_info = fetcher.get_stock_info()
        historical = fetcher.get_historical_data(period=period)

        result = {
            "stock_info": stock_info,
            "historical_data": historical,
            "period": period,
        }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
