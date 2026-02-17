"""
API Index -- Health check and endpoint listing.
"""

import json


def handler(request):
    """Health check endpoint."""
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

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": body,
    }
