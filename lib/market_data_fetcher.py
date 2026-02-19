"""
Market Data Fetcher

Fetches real-time and historical market data from Yahoo Finance via yfinance.
Supports all global exchanges covered by Yahoo Finance.
"""

import numpy as np
import pandas as pd
import yfinance as yf


def validate_ticker(ticker):
    """Validate a ticker symbol by attempting to fetch recent data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            return False, None
        return True, stock
    except Exception:
        return False, None


class MarketDataFetcher:
    """Fetches and caches market data from Yahoo Finance."""

    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self._spot_price = None
        self._volatility = None
        self._dividend_yield = None
        self._info = None

    def _get_info(self):
        if self._info is None:
            try:
                self._info = self.stock.info
            except Exception:
                self._info = {}
        return self._info

    @property
    def spot_price(self):
        if self._spot_price is None:
            hist = self.stock.history(period="5d")
            if hist.empty:
                raise ValueError(f"No price data available for {self.ticker}")
            self._spot_price = float(hist["Close"].iloc[-1])
        return self._spot_price

    @property
    def historical_volatility(self):
        if self._volatility is None:
            hist = self.stock.history(period="1y")
            if hist.empty or len(hist) < 10:
                raise ValueError(
                    f"Insufficient historical data for {self.ticker}"
                )
            returns = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
            self._volatility = float(returns.std() * np.sqrt(252))
        return self._volatility

    @property
    def dividend_yield(self):
        if self._dividend_yield is None:
            try:
                info = self._get_info()
                self._dividend_yield = float(info.get("dividendYield", 0) or 0)
            except Exception:
                self._dividend_yield = 0.0
        return self._dividend_yield

    def get_risk_free_rate(self):
        """Fetch risk-free rate from 13-week Treasury Bill."""
        try:
            treasury = yf.Ticker("^IRX")
            hist = treasury.history(period="5d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1] / 100)
        except Exception:
            pass
        return 0.05  # Default fallback

    def get_stock_info(self):
        """Get summary info about the stock."""
        info = self._get_info()
        return {
            "ticker": self.ticker,
            "name": info.get("longName", info.get("shortName", self.ticker)),
            "exchange": info.get("exchange", "N/A"),
            "currency": info.get("currency", "USD"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", None),
            "spot_price": self.spot_price,
            "historical_volatility": self.historical_volatility,
            "dividend_yield": self.dividend_yield,
            "risk_free_rate": self.get_risk_free_rate(),
        }

    def get_historical_data(self, period="1y", interval="1d"):
        """Get historical OHLCV data."""
        hist = self.stock.history(period=period, interval=interval)
        if hist.empty:
            return []
        hist.index = hist.index.tz_localize(None)
        records = []
        for date, row in hist.iterrows():
            records.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                }
            )
        return records

    def get_options_expiries(self):
        """Get available option expiry dates."""
        try:
            return list(self.stock.options)
        except Exception:
            return []

    def get_options_chain(self, expiry=None):
        """Get the full options chain for a given expiry."""
        try:
            expiries = self.get_options_expiries()
            if not expiries:
                return {"expiries": [], "calls": [], "puts": []}
            if expiry is None or expiry not in expiries:
                expiry = expiries[0]
            chain = self.stock.option_chain(expiry)
            calls = self._chain_to_records(chain.calls)
            puts = self._chain_to_records(chain.puts)
            return {
                "expiries": expiries,
                "selected_expiry": expiry,
                "calls": calls,
                "puts": puts,
            }
        except Exception as e:
            return {
                "expiries": [],
                "calls": [],
                "puts": [],
                "error": str(e),
            }

    def _safe_float(self, val, decimals=None):
        """Safely convert value to float, handling NaN/Inf."""
        try:
            if val is None:
                return None
            f_val = float(val)
            if np.isnan(f_val) or np.isinf(f_val):
                return None
            if decimals is not None:
                return round(f_val, decimals)
            return f_val
        except (ValueError, TypeError):
            return None

    def _chain_to_records(self, df):
        """Convert an options chain DataFrame to a list of dicts."""
        if df is None or df.empty:
            return []
        records = []
        for _, row in df.iterrows():
            record = {
                "strike": self._safe_float(row.get("strike"), 2),
                "lastPrice": self._safe_float(row.get("lastPrice"), 4),
                "bid": self._safe_float(row.get("bid"), 4),
                "ask": self._safe_float(row.get("ask"), 4),
                "volume": int(row.get("volume", 0)) if pd.notna(row.get("volume")) else 0,
                "openInterest": int(row.get("openInterest", 0)) if pd.notna(row.get("openInterest")) else 0,
                "impliedVolatility": self._safe_float(row.get("impliedVolatility"), 4),
                "inTheMoney": bool(row.get("inTheMoney", False)),
            }
            records.append(record)
        return records
