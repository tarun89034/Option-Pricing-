"""
Local Development Server

Run this to test the application locally before deploying to Vercel.
Uses Flask to serve the frontend and API endpoints.

Usage:
    pip install flask flask-cors yfinance numpy pandas
    python server.py

Then open http://localhost:5000
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from lib.market_data_fetcher import MarketDataFetcher, validate_ticker
from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("public", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("public", path)


@app.route("/api")
def api_index():
    return jsonify({
        "status": "ok",
        "service": "Option Pricing API",
        "endpoints": [
            {"path": "/api", "method": "GET", "description": "Health check"},
            {"path": "/api/market_data", "method": "GET", "params": "ticker, period"},
            {"path": "/api/price_option", "method": "GET", "params": "ticker, option_type, strike, days_to_expiry"},
            {"path": "/api/options_chain", "method": "GET", "params": "ticker, expiry"},
            {"path": "/api/exchange_rate", "method": "GET", "params": "source, target"},
        ],
    })


@app.route("/api/market_data")
def market_data():
    ticker = request.args.get("ticker")
    period = request.args.get("period", "1y")

    if not ticker:
        return jsonify({"error": "Missing required parameter: ticker"}), 400

    ticker = ticker.strip().upper()
    valid, _ = validate_ticker(ticker)
    if not valid:
        return jsonify({"error": f"Invalid or unsupported ticker: {ticker}"}), 404

    try:
        fetcher = MarketDataFetcher(ticker)
        return jsonify({
            "stock_info": fetcher.get_stock_info(),
            "historical_data": fetcher.get_historical_data(period=period),
            "period": period,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/price_option")
def price_option():
    ticker = request.args.get("ticker")
    option_type = request.args.get("option_type", "call").strip().lower()
    strike_str = request.args.get("strike")
    days_str = request.args.get("days_to_expiry")

    if not ticker:
        return jsonify({"error": "Missing required parameter: ticker"}), 400
    if not days_str:
        return jsonify({"error": "Missing required parameter: days_to_expiry"}), 400
    if option_type not in ("call", "put"):
        return jsonify({"error": "option_type must be 'call' or 'put'"}), 400

    try:
        days_to_expiry = int(days_str)
        if days_to_expiry <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "days_to_expiry must be a positive integer"}), 400

    ticker = ticker.strip().upper()
    valid, _ = validate_ticker(ticker)
    if not valid:
        return jsonify({"error": f"Invalid or unsupported ticker: {ticker}"}), 404

    try:
        fetcher = MarketDataFetcher(ticker)
        S = fetcher.spot_price
        r = fetcher.get_risk_free_rate()
        sigma = fetcher.historical_volatility
        q = fetcher.dividend_yield
        T = days_to_expiry / 365

        K = float(strike_str) if strike_str else S

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
        }

        bs = BlackScholesModel(S, K, T, r, sigma, q)
        bs_results = bs.get_results(option_type)

        n_steps_calc = max(min(int(T * 252), 252), 21)
        mc = MonteCarloModel(S, K, T, r, sigma, q, n_simulations=50000, n_steps=n_steps_calc)
        mc_results = mc.get_results(option_type)

        bn = BinomialModel(S, K, T, r, sigma, q, n_steps=200)
        bn_results = bn.get_results(option_type)

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
        return jsonify({"error": str(e)}), 500


@app.route("/api/options_chain")
def options_chain():
    ticker = request.args.get("ticker")
    expiry = request.args.get("expiry")
    only_expiries = request.args.get("only_expiries", "false").lower() == "true"

    if not ticker:
        return jsonify({"error": "Missing required parameter: ticker"}), 400

    ticker = ticker.strip().upper()
    valid, _ = validate_ticker(ticker)
    if not valid:
        return jsonify({"error": f"Invalid or unsupported ticker: {ticker}"}), 404

    try:
        fetcher = MarketDataFetcher(ticker)
        
        if only_expiries:
             return jsonify({"expiries": fetcher.get_options_expiries()})

        chain = fetcher.get_options_chain(expiry=expiry)
        chain["ticker"] = ticker
        chain["spot_price"] = round(fetcher.spot_price, 2)
        return jsonify(chain)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/exchange_rate")
def exchange_rate():
    try:
        source = request.args.get("source", "USD").upper()
        target = request.args.get("target", "USD").upper()
        
        # Helper to get USD rate for a currency
        def get_usd_rate(currency):
             if currency == "USD": return 1.0
             majors = ["EUR", "GBP", "AUD", "NZD"]
             import yfinance as yf
             if currency in majors:
                 t = f"{currency}=X"
                 h = yf.Ticker(t).history(period="1d")
                 if not h.empty:
                     return float(h["Close"].iloc[-1])
             else:
                 t = f"{currency}=X"
                 h = yf.Ticker(t).history(period="1d")
                 if not h.empty:
                     val = float(h["Close"].iloc[-1])
                     if val == 0: return 0
                     return 1.0 / val
             return None

        if source == target:
            rate = 1.0
        else:
            rate_s = get_usd_rate(source)
            rate_t = get_usd_rate(target)
            
            if rate_s is None or rate_t is None:
                 return jsonify({"error": "Could not determine exchange rate"}), 404
            
            rate = rate_s / rate_t

        return jsonify({
            "source": source,
            "target": target,
            "rate": rate,
            "timestamp": "latest"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n  Option Pricing -- Local Development Server")
    print("  http://localhost:5000\n")
    app.run(debug=True, port=5000)
