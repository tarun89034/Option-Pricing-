# Option Pricing -- Quantitative Analysis Platform

A professional web application for pricing financial options using three quantitative models: **Black-Scholes**, **Monte Carlo simulation**, and **Binomial Tree**. Features interactive historical data dashboards, real-time options chain data, and comprehensive Greeks analysis.

---

## Features

### Pricing Calculator
- **Black-Scholes Model** -- Analytical European option pricing with complete Greeks (Delta, Gamma, Theta, Vega, Rho)
- **Monte Carlo Simulation** -- Prices European, Asian (arithmetic/geometric), Lookback (floating strike), and Barrier (knock-in/knock-out) options using antithetic variates for variance reduction
- **Binomial Tree (CRR)** -- Cox-Ross-Rubinstein model for both European and American options with early exercise valuation
- **Model Convergence** -- Automatic comparison across models with deviation metrics
- **Moneyness Detection** -- Classifies options as ITM, ATM, or OTM

### Historical Dashboard
- Interactive price history chart (Chart.js)
- Volume analysis with color-coded bars
- Stock fundamentals (sector, market cap, exchange)
- Sortable historical data table

### Options Chain
- Real-time options chain from Yahoo Finance
- **50x Faster Loading** -- Optimised to fetch expiry dates instantly
- Calls and puts with bid/ask, volume, open interest, and implied volatility
- In-the-money highlighting
- Sortable columns

### Currency Conversion
- **Real-Time FX Rates** -- Convert all prices, strikes, and premiums instantly
- Supports: USD ($), EUR (€), GBP (£), INR (₹), JPY (¥), AUD (A$), CAD (C$), CNY (¥)
- Automatic cross-rate calculation (e.g., converting INR stock to USD)

### Global Markets Explorer
Built-in interactive explorer covering **30+ countries** across 6 regions with click-to-load ticker selection:

| Region | Countries |
|--------|----------|
| **North America** | United States (NYSE, NASDAQ), Canada (TSX), Mexico (BMV) |
| **South America** | Brazil (B3), Argentina (BCBA), Chile (BCS), Colombia (BVC) |
| **Europe** | UK (LSE), Germany (XETRA), France (Euronext Paris), Switzerland (SIX), Netherlands, Spain, Italy, Sweden, Norway |
| **Asia** | India (NSE, BSE), Japan (TSE), China (SSE, SZSE, HKEX), South Korea (KRX), Taiwan (TWSE), Singapore (SGX), Thailand, Malaysia, Indonesia, Philippines, Vietnam, Israel, Saudi Arabia |
| **Africa** | South Africa (JSE), Nigeria (NGX), Egypt (EGX), Kenya (NSE), Morocco (Casablanca SE) |
| **Oceania** | Australia (ASX), New Zealand (NZX) |

---

## Architecture

```
Option pricing/
|-- api/                         # Vercel serverless functions (Python)
|   |-- index.py                 # Health check
|   |-- market_data.py           # Stock info + historical prices
|   |-- price_option.py          # Multi-model option pricing
|   |-- options_chain.py         # Real-time options chain
|
|-- public/                      # Static frontend
|   |-- index.html               # SPA entry point
|   |-- css/styles.css           # Dark minimalistic design system
|   |-- js/app.js                # Application controller
|   |-- js/api.js                # API communication layer
|   |-- js/markets.js            # Global markets data (30+ countries)
|   |-- js/charts.js             # Chart.js visualizations
|   |-- js/utils.js              # Formatting utilities
|
|-- lib/                         # Shared Python modules
|   |-- pricing_models.py        # BS, MC, Binomial implementations
|   |-- market_data_fetcher.py   # yfinance data fetching
|
|-- server.py                    # Flask local dev server
|-- vercel.json                  # Vercel deployment config
|-- requirements.txt             # Python dependencies
```

---

## API Reference

### `GET /api/market_data`
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `ticker`  | Yes      | --      | Stock ticker symbol |
| `period`  | No       | `1y`    | History period (1mo, 3mo, 6mo, 1y, 2y, 5y) |

### `GET /api/price_option`
| Parameter        | Required | Default | Description |
|------------------|----------|---------|-------------|
| `ticker`         | Yes      | --      | Stock ticker symbol |
| `option_type`    | No       | `call`  | `call` or `put` |
| `strike`         | No       | ATM     | Strike price (defaults to spot) |
| `days_to_expiry` | Yes      | --      | Days until expiration |

### `GET /api/options_chain`
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `ticker`  | Yes      | --      | Stock ticker symbol |
| `expiry`  | No       | Nearest | Expiry date (YYYY-MM-DD) |
| `only_expiries` | No | `false` | Set `true` to fetch only expiry dates (fast) |

### `GET /api/exchange_rate`
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `source`  | No       | `USD`   | Source currency code (e.g. USD) |
| `target`  | No       | `USD`   | Target currency code (e.g. INR) |

---

## Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# Install dependencies
pip install flask flask-cors yfinance numpy scipy pandas

# Run the development server
python server.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Deploy to Vercel

### Prerequisites
- [Vercel CLI](https://vercel.com/docs/cli) or a Vercel account

### Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

The application uses `vercel.json` to route API requests to Python serverless functions and serve frontend assets statically. No build step is required.

---

## Mathematical Models

### Black-Scholes-Merton
Closed-form solution for European options under assumptions of log-normal returns, constant volatility, and no dividends (extended with Merton's continuous dividend yield adjustment).

### Monte Carlo Simulation
Generates price paths using Geometric Brownian Motion with antithetic variates for variance reduction. Supports path-dependent options (Asian, Lookback, Barrier) that lack closed-form solutions.

### Binomial Tree (Cox-Ross-Rubinstein)
Discrete-time lattice model that converges to Black-Scholes as steps increase. Uniquely capable of pricing American options with early exercise by comparing continuation value against intrinsic value at each node.

---

## Data Source

All market data is sourced from **Yahoo Finance** via the [yfinance](https://github.com/ranaroussi/yfinance) Python library. Data is real-time or delayed per exchange rules. Options chain availability varies by market -- US markets have the most comprehensive coverage.

---

## License

MIT
