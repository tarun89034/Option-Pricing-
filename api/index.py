import os
import sys
import json
import traceback
from flask import Flask, request, jsonify

# Add project root to sys.path so lib/ can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

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
@app.route('/api')
def health():
    """Health check endpoint with import diagnostics."""
    diagnostics = {
        "status": "starting",
        "python_version": sys.version,
    }

    try:
        import numpy as np
        diagnostics["numpy"] = np.__version__
        import pandas as pd
        diagnostics["pandas"] = pd.__version__
        import yfinance as yf
        diagnostics["yfinance"] = yf.__version__
        from lib.market_data_fetcher import MarketDataFetcher
        diagnostics["fetcher"] = "ok"
        from lib.pricing_models import BlackScholesModel
        diagnostics["models"] = "ok"

        diagnostics["status"] = "ok"
        return jsonify(diagnostics)
    except Exception as e:
        diagnostics["status"] = "error"
        diagnostics["error"] = str(e)
        diagnostics["traceback"] = traceback.format_exc()
        return jsonify(diagnostics), 500


@app.route('/api/market_data', methods=['GET', 'OPTIONS'])
def market_data():
    if request.method == 'OPTIONS':
        return '', 204
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


@app.route('/api/price_option', methods=['GET', 'OPTIONS'])
def price_option():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        from lib.market_data_fetcher import MarketDataFetcher
        from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel

        ticker = request.args.get("ticker")
        days_str = request.args.get("days_to_expiry")
        if not ticker or not days_str:
            return jsonify({"error": "Missing parameters"}), 400

        ticker = ticker.strip().upper()
        days_to_expiry = int(days_str)
        fetcher = MarketDataFetcher(ticker)
        S = fetcher.spot_price
        K = float(request.args.get("strike")) if request.args.get("strike") else S
        T = days_to_expiry / 365
        option_type = request.args.get("option_type", "call").lower()
        r = fetcher.get_risk_free_rate()
        sigma = fetcher.historical_volatility
        q = fetcher.dividend_yield

        # Moneyness
        moneyness = S / K
        if option_type == "call":
            ms = "ITM" if moneyness > 1.02 else ("OTM" if moneyness < 0.98 else "ATM")
        else:
            ms = "ITM" if moneyness < 0.98 else ("OTM" if moneyness > 1.02 else "ATM")

        market_data = {
            "ticker": ticker,
            "name": fetcher.get_stock_info().get("name", ticker),
            "spot_price": round(S, 4),
            "strike_price": round(K, 4),
            "days_to_expiry": days_to_expiry,
            "time_to_expiry_years": round(T, 6),
            "risk_free_rate": round(r, 6),
            "volatility": round(sigma, 6),
            "dividend_yield": round(q, 6),
            "option_type": option_type.upper(),
            "moneyness": ms,
            "moneyness_ratio": round(moneyness, 4),
            "currency": fetcher.get_stock_info().get("currency", "USD"),
        }

        bs = BlackScholesModel(S, K, T, r, sigma, q)
        bs_results = bs.get_results(option_type)

        # Use reduced simulations/steps for serverless environment
        # to avoid timeout and memory issues
        mc = MonteCarloModel(S, K, T, r, sigma, q, n_simulations=10000, n_steps=50)
        mc_results = mc.get_results(option_type)

        bn = BinomialModel(S, K, T, r, sigma, q, n_steps=50)
        bn_results = bn.get_results(option_type)

        # Convergence data expected by frontend
        bs_price = bs_results["price"]
        bin_eu = bn_results["european_price"]
        mc_eu = mc_results["european"]["price"]

        convergence = {
            "bs_vs_binomial": {
                "diff": round(abs(bs_price - bin_eu), 6),
                "pct": round(abs(bs_price - bin_eu) / bs_price * 100, 4) if bs_price != 0 else 0,
            },
            "bs_vs_monte_carlo": {
                "diff": round(abs(bs_price - mc_eu), 6),
                "pct": round(abs(bs_price - mc_eu) / bs_price * 100, 4) if bs_price != 0 else 0,
            },
        }

        return jsonify({
            "market_data": market_data,
            "black_scholes": bs_results,
            "monte_carlo": mc_results,
            "binomial": bn_results,
            "convergence": convergence,
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route('/api/options_chain', methods=['GET', 'OPTIONS'])
def options_chain():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        from lib.market_data_fetcher import MarketDataFetcher
        ticker = request.args.get("ticker")
        if not ticker:
            return jsonify({"error": "Missing ticker"}), 400

        fetcher = MarketDataFetcher(ticker.strip().upper())
        if request.args.get("only_expiries") == "true":
            return jsonify({"expiries": fetcher.get_options_expiries()})
        return jsonify(fetcher.get_options_chain(expiry=request.args.get("expiry")))
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route('/api/exchange_rate', methods=['GET', 'OPTIONS'])
def exchange_rate():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        import yfinance as yf
        source = request.args.get("source", "USD").upper()
        target = request.args.get("target", "USD").upper()
        if source == target:
            return jsonify({"rate": 1.0, "source": source, "target": target})

        t_pair = f"{source}{target}=X" if source != "USD" else f"{target}=X"
        ticker = yf.Ticker(t_pair)
        h = ticker.history(period="1d")
        rate = float(h["Close"].iloc[-1]) if not h.empty else 1.0
        return jsonify({"source": source, "target": target, "rate": rate})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
