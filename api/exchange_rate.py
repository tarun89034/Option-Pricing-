"""
Exchange Rate API Endpoint

Returns real-time exchange rates from Yahoo Finance.
"""

import json
import sys
import os
import yfinance as yf
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def handler(request):
    """Handle exchange rate requests."""
    if hasattr(request, "method") and request.method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        if hasattr(request, "url"):
            parsed = urlparse(request.url)
            params = parse_qs(parsed.query)
        elif hasattr(request, "args"):
            params = {k: [v] for k, v in request.args.items()}
        else:
            params = {}

        source = params.get("source", ["USD"])[0].upper()
        target = params.get("target", ["USD"])[0].upper()

        if source == target:
            rate = 1.0
        else:
            if source == "USD":
                # Direct quote: e.g. USDINR=X
                ticker = f"{target}=X"
                # Some pairs are inverted in common parlance but YF usually has USDxxx=X or xxx=X
                # For major pairs it might be EUR=X (EURUSD) or GBP=X (GBPUSD) which is inverse of what we want if source is USD
                # But actually YF `INR=X` is USD to INR. `EUR=X` is USD to EUR.
                # Let's try standard format for non-USD base? No, usually YF is USD base.
                # `INR=X` -> rate USD to INR.
                # `EUR=X` -> rate USD to EUR.
                ticker = f"{target}=X"
                
                # Exception: Major pairs where USD is quote currency?
                # Actually EUR=X is EUR/USD rate. 
                # Let's use a robust approach: try "{source}{target}=X" first.
                
                pair = f"{source}{target}=X"
                stock = yf.Ticker(pair)
                hist = stock.history(period="1d")
                
                if hist.empty:
                    # Try inverted if not found? Or just try target=X if source is USD?
                    # YF conventions are messy. 
                    # Let's stick to a known map or try direct construction.
                    # 'INR=X' is USD/INR. 'EURUSD=X' is EUR/USD. 
                    if source == "USD":
                        pair = f"{target}=X" # e.g. INR=X
                        stock = yf.Ticker(pair)
                        hist = stock.history(period="1d")
                    elif target == "USD":
                        pair = f"{source}=X" # e.g. EUR=X (EURUSD) 
                        # If pair is EUR=X, close price is 1.05 (EUR to USD). 
                        # So if we want AUD -> USD, AUD=X is AUD/USD.
                        stock = yf.Ticker(pair)
                        hist = stock.history(period="1d")
                    else:
                        # Cross rate? Calculate via USD.
                        # Too complex for this simple endpoint. Let's stick to USD base for now.
                        # User wants USD -> INR mostly.
                        return {
                            "statusCode": 400,
                            "headers": CORS_HEADERS,
                            "body": json.dumps({"error": "Currently only supports conversion to/from USD."}),
                        }

                if hist.empty:
                     return {
                        "statusCode": 404,
                        "headers": CORS_HEADERS,
                        "body": json.dumps({"error": f"Could not find exchange rate for {source}/{target} (tried {pair})"}),
                    }
                
                rate = float(hist["Close"].iloc[-1])
                # If we used target=X (e.g. INR=X), value is e.g. 83.0 (1 USD = 83 INR). Correct.
                # If we used source=X (e.g. EUR=X) for target=USD, value is 1.05 (1 EUR = 1.05 USD). Correct.
            
            else:
                # Source is not USD. And target is not USD (handled above).
                # Wait, my logic above had 'elif target == USD'.
                # Let's refine.
                # Case 1: USD -> INR. ticker='INR=X'. Price ~84. Rate = Price.
                # Case 2: EUR -> USD. ticker='EUR=X'. Price ~1.05. Rate = Price.
                # Case 3: INR -> USD. ticker='INR=X'. Price ~84. Rate = 1/Price.
                # Case 4: EUR -> INR. Cross rate.
                
                # Simplified approach: Always fetch USD-pair for both and calculate cross.
                # Get rate S_USD (1 Source = S_USD USD)
                # Get rate T_USD (1 Target = T_USD USD)
                # Rate S->T = S_USD / T_USD.
                
                def get_usd_rate(currency):
                     if currency == "USD": return 1.0
                     # Try direct: EUR=X means 1 EUR = x USD? 
                     # No, Actually:
                     # EUR=X -> 1.04 (USD per EUR).  (Quote is USD)
                     # INR=X -> 86.8 (INR per USD).  (Quote is INR)
                     # JPY=X -> 153 (JPY per USD).
                     # GBP=X -> 1.25 (USD per GBP).
                     
                     # Major currencies (EUR, GBP, AUD, NZD) are usually base currency.
                     # Others (INR, JPY, CAD, CHF) are usually quote currency.
                     
                     majors = ["EUR", "GBP"]
                     if currency in majors:
                         t = f"{currency}=X"
                         h = yf.Ticker(t).history(period="1d")
                         if not h.empty:
                             return float(h["Close"].iloc[-1])
                     else:
                         t = f"{currency}=X"
                         h = yf.Ticker(t).history(period="1d")
                         if not h.empty:
                             # This gives currency per 1 USD.
                             # We need USD per 1 currency.
                             val = float(h["Close"].iloc[-1])
                             if val == 0: return 0
                             return 1.0 / val
                     return None

                rate_s = get_usd_rate(source)
                rate_t = get_usd_rate(target)
                
                if rate_s is None or rate_t is None:
                     return {
                        "statusCode": 404,
                        "headers": CORS_HEADERS,
                        "body": json.dumps({"error": "Could not determine exchange rate."}),
                    }
                
                rate = rate_s / rate_t

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "source": source,
                "target": target,
                "rate": rate,
                "timestamp":  "latest" 
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
