import os
import sys
import json
import traceback
from flask import Flask, request, jsonify

# Configuration
app = Flask(__name__)

# Add absolute root path to sys.path
# This is safe to do at top level
try:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
except Exception:
    pass

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
    """
    Super-safe health check. Try-catch inside the route 
    to see exactly which import is failing.
    """
    diagnostics = {
        "status": "starting",
        "python_version": sys.version,
        "env": dict(os.environ),
        "path": sys.path
    }
    
    try:
        import numpy as np
        diagnostics["numpy"] = "ok"
        import pandas as pd
        diagnostics["pandas"] = "ok"
        import yfinance as yf
        diagnostics["yfinance"] = "ok"
        from lib.market_data_fetcher import MarketDataFetcher
        diagnostics["fetcher"] = "ok"
        from lib.pricing_models import BlackScholesModel
        diagnostics["models"] = "ok"
        
        return jsonify({"status": "ok", "diagnostics": diagnostics})
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e), 
            "traceback": traceback.format_exc(),
            "diagnostics": diagnostics
        }), 500

@app.route('/api/market_data', methods=['GET'])
def market_data():
    try:
        from lib.market_data_fetcher import MarketDataFetcher, validate_ticker
        ticker = request.args.get("ticker")
        period = request.args.get("period", "1y")
        if not ticker:
            return jsonify({"error": "Missing ticker"}), 400
        
        fetcher = MarketDataFetcher(ticker.strip().upper())
        return jsonify({
            "stock_info": fetcher.get_stock_info(),
            "historical_data": fetcher.get_historical_data(period=period)
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/price_option', methods=['GET'])
def price_option():
    try:
        from lib.market_data_fetcher import MarketDataFetcher
        from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel
        
        ticker = request.args.get("ticker")
        days_str = request.args.get("days_to_expiry")
        if not ticker or not days_str:
            return jsonify({"error": "Missing parameters"}), 400
            
        fetcher = MarketDataFetcher(ticker.strip().upper())
        S = fetcher.spot_price
        K = float(request.args.get("strike")) if request.args.get("strike") else S
        T = int(days_str) / 365
        option_type = request.args.get("option_type", "call").lower()
        
        bs = BlackScholesModel(S, K, T, fetcher.get_risk_free_rate(), fetcher.historical_volatility, fetcher.dividend_yield)
        
        # Reduced MC sims for faster lambda response
        mc = MonteCarloModel(S, K, T, fetcher.get_risk_free_rate(), fetcher.historical_volatility, fetcher.dividend_yield, n_simulations=10000)
        bn = BinomialModel(S, K, T, fetcher.get_risk_free_rate(), fetcher.historical_volatility, fetcher.dividend_yield, n_steps=50)

        return jsonify({
            "market_data": {"spot": S, "ticker": ticker.upper(), "currency": "USD"},
            "black_scholes": bs.get_results(option_type),
            "monte_carlo": mc.get_results(option_type),
            "binomial": bn.get_results(option_type)
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/options_chain', methods=['GET'])
def options_chain():
    try:
        from lib.market_data_fetcher import MarketDataFetcher
        ticker = request.args.get("ticker")
        if not ticker: return jsonify({"error": "Missing ticker"}), 400
        
        fetcher = MarketDataFetcher(ticker.strip().upper())
        if request.args.get("only_expiries") == "true":
            return jsonify({"expiries": fetcher.get_options_expiries()})
        return jsonify(fetcher.get_options_chain(expiry=request.args.get("expiry")))
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/exchange_rate', methods=['GET'])
def exchange_rate():
    try:
        import yfinance as yf
        source = request.args.get("source", "USD").upper()
        target = request.args.get("target", "USD").upper()
        if source == target: return jsonify({"rate": 1.0, "source": source, "target": target})
        
        t_pair = f"{source}{target}=X" if source != "USD" else f"{target}=X"
        ticker = yf.Ticker(t_pair)
        h = ticker.history(period="1d")
        rate = float(h["Close"].iloc[-1]) if not h.empty else 1.0
        return jsonify({"source": source, "target": target, "rate": rate})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# Vercel requirement
handler = app
