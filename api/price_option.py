"""
Option Pricing API Endpoint

Prices an option using Black-Scholes, Monte Carlo, and Binomial Tree models.
"""

import json
import sys
import os
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.market_data_fetcher import MarketDataFetcher, validate_ticker
from lib.pricing_models import BlackScholesModel, MonteCarloModel, BinomialModel


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
            option_type = params.get("option_type", ["call"])[0]
            strike_str = params.get("strike", [None])[0]
            days_str = params.get("days_to_expiry", [None])[0]

            # Validate inputs
            if not ticker or not days_str:
                self._send_response(400, {"error": "Missing required parameters: ticker and days_to_expiry"})
                return

            ticker = ticker.strip().upper()
            option_type = option_type.strip().lower()
            if option_type not in ("call", "put"):
                self._send_response(400, {"error": "option_type must be 'call' or 'put'"})
                return

            try:
                days_to_expiry = int(days_str)
                if days_to_expiry <= 0: raise ValueError
            except (ValueError, TypeError):
                self._send_response(400, {"error": "days_to_expiry must be a positive integer"})
                return

            valid, _ = validate_ticker(ticker)
            if not valid:
                self._send_response(404, {"error": f"Invalid or unsupported ticker: {ticker}"})
                return

            # Fetch market data
            fetcher = MarketDataFetcher(ticker)
            S = fetcher.spot_price
            r = fetcher.get_risk_free_rate()
            sigma = fetcher.historical_volatility
            q = fetcher.dividend_yield
            T = days_to_expiry / 365

            # Determine strike
            if strike_str is not None:
                try:
                    K = float(strike_str)
                    if K <= 0: raise ValueError
                except (ValueError, TypeError):
                    self._send_response(400, {"error": "strike must be a positive number"})
                    return
            else:
                K = S  # ATM

            # Calculate moneyness
            moneyness = S / K
            moneyness_status = "ATM"
            if option_type == "call":
                if moneyness > 1.02: moneyness_status = "ITM"
                elif moneyness < 0.98: moneyness_status = "OTM"
            else:
                if moneyness < 0.98: moneyness_status = "ITM"
                elif moneyness > 1.02: moneyness_status = "OTM"

            # Market data summary
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
                "moneyness": moneyness_status,
                "moneyness_ratio": round(moneyness, 4),
                "currency": fetcher.get_stock_info().get("currency", "USD")
            }

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

            # Convergence
            bs_price = bs_results["price"]
            bin_eu_price = bin_results["european_price"]
            mc_eu_price = mc_results["european"]["price"]

            convergence = {
                "bs_vs_binomial": {
                    "diff": round(abs(bs_price - bin_eu_price), 6),
                    "pct": round(abs(bs_price - bin_eu_price) / bs_price * 100, 4) if bs_price != 0 else 0,
                },
                "bs_vs_monte_carlo": {
                    "diff": round(abs(bs_price - mc_eu_price), 6),
                    "pct": round(abs(bs_price - mc_eu_price) / bs_price * 100, 4) if bs_price != 0 else 0,
                },
            }

            result = {
                "market_data": market_data,
                "black_scholes": bs_results,
                "monte_carlo": mc_results,
                "binomial": bin_results,
                "convergence": convergence,
            }

            self._send_response(200, result)

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, code, data):
        self.send_response(code)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

