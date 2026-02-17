import json
import os
import sys
from flask import Flask, request, jsonify

# Add absolute root path to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from lib.market_data_fetcher import MarketDataFetcher, validate_ticker
from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel

app = Flask(__name__)

# Manual CORS handling to remove flask-cors dependency
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/api/health', methods=['GET'])
@app.route('/api/', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "Option Pricing API (Flask Monolith Optimized)"
    })

@app.route('/api/market_data', methods=['GET'])
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
        stock_info = fetcher.get_stock_info()
        historical = fetcher.get_historical_data(period=period)
        return jsonify({
            "stock_info": stock_info,
            "historical_data": historical,
            "period": period,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/price_option', methods=['GET'])
def price_option():
    ticker = request.args.get("ticker")
    option_type = request.args.get("option_type", "call").lower()
    strike_str = request.args.get("strike")
    days_str = request.args.get("days_to_expiry")

    if not ticker or not days_str:
        return jsonify({"error": "Missing required parameters: ticker and days_to_expiry"}), 400

    try:
        days_to_expiry = int(days_str)
        if days_to_expiry <= 0: raise ValueError
    except:
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

        if strike_str:
            K = float(strike_str)
        else:
            K = S

        # Black-Scholes
        bs_model = BlackScholesModel(S, K, T, r, sigma, q)
        bs_results = bs_model.get_results(option_type)

        # Monte Carlo
        n_steps_calc = max(min(int(T * 252), 252), 21)
        mc_model = MonteCarloModel(S, K, T, r, sigma, q, n_simulations=50000, n_steps=n_steps_calc)
        mc_results = mc_model.get_results(option_type)

        # Binomial Tree
        bin_model = BinomialModel(S, K, T, r, sigma, q, n_steps=200)
        bin_results = bin_model.get_results(option_type)

        # Market data summary
        market_data = {
            "ticker": ticker,
            "name": fetcher.get_stock_info().get("name", ticker),
            "spot_price": round(S, 4),
            "strike_price": round(K, 4),
            "days_to_expiry": days_to_expiry,
            "option_type": option_type.upper(),
            "currency": fetcher.get_stock_info().get("currency", "USD")
        }

        return jsonify({
            "market_data": market_data,
            "black_scholes": bs_results,
            "monte_carlo": mc_results,
            "binomial": bin_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/options_chain', methods=['GET'])
def options_chain():
    ticker = request.args.get("ticker")
    expiry = request.args.get("expiry")
    only_expiries = request.args.get("only_expiries", "false").lower() == "true"

    if not ticker:
        return jsonify({"error": "Missing required parameter: ticker"}), 400

    ticker = ticker.strip().upper()
    try:
        fetcher = MarketDataFetcher(ticker)
        if only_expiries:
            return jsonify({"expiries": fetcher.get_options_expiries()})
        
        chain_data = fetcher.get_options_chain(expiry=expiry)
        chain_data["ticker"] = ticker
        chain_data["spot_price"] = round(fetcher.spot_price, 2)
        return jsonify(chain_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exchange_rate', methods=['GET'])
def exchange_rate():
    import yfinance as yf
    source = request.args.get("source", "USD").upper()
    target = request.args.get("target", "USD").upper()

    if source == target:
        return jsonify({"source": source, "target": target, "rate": 1.0})

    try:
        def get_usd_rate(currency):
            if currency == "USD": return 1.0
            majors = ["EUR", "GBP"]
            t = f"{currency}=X"
            h = yf.Ticker(t).history(period="1d")
            if not h.empty:
                val = float(h["Close"].iloc[-1])
                return val if currency in majors else 1.0 / val if val != 0 else 0
            return None

        rate_s = get_usd_rate(source)
        rate_t = get_usd_rate(target)
        if rate_s is None or rate_t is None:
            return jsonify({"error": f"Could not determine rate for {source}/{target}"}), 404

        return jsonify({
            "source": source,
            "target": target,
            "rate": rate_s / rate_t,
            "timestamp": "latest"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requirements
handler = app
