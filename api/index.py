import os
import sys
import json
import traceback

# 1. Global Diagnostic Catching
# This ensures that even if imports fail, Vercel still starts the process 
# and we can see what exactly caused the failure.
try:
    from flask import Flask, request, jsonify
    
    # Add absolute root path to sys.path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Attempt core imports
    from lib.market_data_fetcher import MarketDataFetcher, validate_ticker
    from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel
    import yfinance as yf
    
    # Configure yfinance to avoid multi-threading issues and use /tmp for caching if needed
    # (Note: newer yfinance versions use different caching mechanisms, but this is a safe precaution)
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    IMPORT_ERROR = None
except Exception:
    IMPORT_ERROR = traceback.format_exc()

app = Flask(__name__)

# Manual CORS handling
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/api/health')
@app.route('/api/')
def health():
    if IMPORT_ERROR:
        return jsonify({
            "status": "error",
            "message": "Initialization failed",
            "error_details": IMPORT_ERROR,
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }), 500
    return jsonify({
        "status": "ok",
        "service": "Option Pricing API (Diagnostics Enabled)",
        "imports": "successful"
    })

# Main handlers (only if imports were successful)
def register_routes():
    if IMPORT_ERROR: return

    @app.route('/api/market_data', methods=['GET'])
    def market_data():
        ticker = request.args.get("ticker")
        period = request.args.get("period", "1y")
        if not ticker:
            return jsonify({"error": "Missing ticker"}), 400
        try:
            fetcher = MarketDataFetcher(ticker.strip().upper())
            return jsonify({
                "stock_info": fetcher.get_stock_info(),
                "historical_data": fetcher.get_historical_data(period=period)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/price_option', methods=['GET'])
    def price_option():
        ticker = request.args.get("ticker")
        days_str = request.args.get("days_to_expiry")
        if not ticker or not days_str:
            return jsonify({"error": "Missing parameters"}), 400
        try:
            fetcher = MarketDataFetcher(ticker.strip().upper())
            S = fetcher.spot_price
            K = float(request.args.get("strike")) if request.args.get("strike") else S
            T = int(days_str) / 365
            option_type = request.args.get("option_type", "call").lower()
            
            bs = BlackScholesModel(S, K, T, fetcher.get_risk_free_rate(), fetcher.historical_volatility, fetcher.dividend_yield)
            return jsonify({
                "market_data": {"spot": S, "ticker": ticker.upper()},
                "black_scholes": bs.get_results(option_type)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/options_chain', methods=['GET'])
    def options_chain():
        ticker = request.args.get("ticker")
        if not ticker: return jsonify({"error": "Missing ticker"}), 400
        try:
            fetcher = MarketDataFetcher(ticker.strip().upper())
            if request.args.get("only_expiries") == "true":
                return jsonify({"expiries": fetcher.get_options_expiries()})
            return jsonify(fetcher.get_options_chain(expiry=request.args.get("expiry")))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/exchange_rate', methods=['GET'])
    def exchange_rate():
        source = request.args.get("source", "USD").upper()
        target = request.args.get("target", "USD").upper()
        if source == target: return jsonify({"rate": 1.0})
        try:
            t_pair = f"{source}{target}=X" if source != "USD" else f"{target}=X"
            h = yf.Ticker(t_pair).history(period="1d")
            rate = float(h["Close"].iloc[-1]) if not h.empty else 1.0
            return jsonify({"source": source, "target": target, "rate": rate})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

register_routes()

# Vercel requirement
handler = app
