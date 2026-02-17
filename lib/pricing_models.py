"""
Option Pricing Models

Implements Black-Scholes, Monte Carlo, and Binomial Tree pricing models
for European, American, Asian, Lookback, and Barrier options.
"""

import numpy as np
from scipy.stats import norm


class BlackScholesModel:
    """
    Black-Scholes-Merton model for European option pricing.

    Parameters:
        S: Spot price
        K: Strike price
        T: Time to expiry (years)
        r: Risk-free rate
        sigma: Volatility
        q: Dividend yield
    """

    def __init__(self, S, K, T, r, sigma, q=0):
        self.S = S
        self.K = K
        self.T = max(T, 1e-10)
        self.r = r
        self.sigma = max(sigma, 1e-10)
        self.q = q
        self._calculate_d1_d2()

    def _calculate_d1_d2(self):
        sqrt_T = np.sqrt(self.T)
        self.d1 = (
            np.log(self.S / self.K)
            + (self.r - self.q + 0.5 * self.sigma**2) * self.T
        ) / (self.sigma * sqrt_T)
        self.d2 = self.d1 - self.sigma * sqrt_T

    def call_price(self):
        return self.S * np.exp(-self.q * self.T) * norm.cdf(
            self.d1
        ) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)

    def put_price(self):
        return self.K * np.exp(-self.r * self.T) * norm.cdf(
            -self.d2
        ) - self.S * np.exp(-self.q * self.T) * norm.cdf(-self.d1)

    def price(self, option_type="call"):
        return self.call_price() if option_type.lower() == "call" else self.put_price()

    def delta(self, option_type="call"):
        if option_type.lower() == "call":
            return float(np.exp(-self.q * self.T) * norm.cdf(self.d1))
        return float(np.exp(-self.q * self.T) * (norm.cdf(self.d1) - 1))

    def gamma(self):
        return float(
            (np.exp(-self.q * self.T) * norm.pdf(self.d1))
            / (self.S * self.sigma * np.sqrt(self.T))
        )

    def theta(self, option_type="call"):
        term1 = -(
            self.S * self.sigma * np.exp(-self.q * self.T) * norm.pdf(self.d1)
        ) / (2 * np.sqrt(self.T))
        if option_type.lower() == "call":
            term2 = self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(self.d1)
            term3 = -self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        else:
            term2 = -self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(-self.d1)
            term3 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
        return float((term1 + term2 + term3) / 365)

    def vega(self):
        return float(
            self.S
            * np.exp(-self.q * self.T)
            * np.sqrt(self.T)
            * norm.pdf(self.d1)
            / 100
        )

    def rho(self, option_type="call"):
        if option_type.lower() == "call":
            return float(
                self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2) / 100
            )
        return float(
            -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2) / 100
        )

    def get_all_greeks(self, option_type="call"):
        return {
            "delta": self.delta(option_type),
            "gamma": self.gamma(),
            "theta": self.theta(option_type),
            "vega": self.vega(),
            "rho": self.rho(option_type),
        }

    def get_results(self, option_type="call"):
        return {
            "price": float(self.price(option_type)),
            "greeks": self.get_all_greeks(option_type),
        }


class MonteCarloModel:
    """
    Monte Carlo simulation for option pricing.

    Supports: European, Asian, Lookback, and Barrier options.
    Uses antithetic variates for variance reduction.
    """

    def __init__(self, S, K, T, r, sigma, q=0, n_simulations=100000, n_steps=252):
        self.S = S
        self.K = K
        self.T = max(T, 1e-10)
        self.r = r
        self.sigma = max(sigma, 1e-10)
        self.q = q
        self.n_simulations = n_simulations
        self.n_steps = n_steps
        self.dt = self.T / n_steps

    def _generate_paths(self, antithetic=True, seed=42):
        np.random.seed(seed)
        n_sims = self.n_simulations // 2 if antithetic else self.n_simulations
        drift = (self.r - self.q - 0.5 * self.sigma**2) * self.dt
        vol = self.sigma * np.sqrt(self.dt)
        Z = np.random.standard_normal((n_sims, self.n_steps))
        if antithetic:
            Z = np.vstack([Z, -Z])
        log_returns = drift + vol * Z
        log_paths = np.cumsum(log_returns, axis=1)
        paths = self.S * np.exp(log_paths)
        paths = np.column_stack([np.full(self.n_simulations, self.S), paths])
        return paths

    def european_option_price(self, option_type="call"):
        paths = self._generate_paths()
        final_prices = paths[:, -1]
        if option_type.lower() == "call":
            payoffs = np.maximum(final_prices - self.K, 0)
        else:
            payoffs = np.maximum(self.K - final_prices, 0)
        discount = np.exp(-self.r * self.T)
        price = discount * np.mean(payoffs)
        std_error = discount * np.std(payoffs) / np.sqrt(self.n_simulations)
        return float(price), float(std_error)

    def asian_option_price(self, option_type="call", averaging="arithmetic"):
        paths = self._generate_paths()
        if averaging == "arithmetic":
            avg_prices = np.mean(paths, axis=1)
        else:
            avg_prices = np.exp(np.mean(np.log(paths), axis=1))
        if option_type.lower() == "call":
            payoffs = np.maximum(avg_prices - self.K, 0)
        else:
            payoffs = np.maximum(self.K - avg_prices, 0)
        discount = np.exp(-self.r * self.T)
        price = discount * np.mean(payoffs)
        std_error = discount * np.std(payoffs) / np.sqrt(self.n_simulations)
        return float(price), float(std_error)

    def lookback_option_price(self, option_type="call"):
        paths = self._generate_paths()
        final_prices = paths[:, -1]
        if option_type.lower() == "call":
            min_prices = np.min(paths, axis=1)
            payoffs = np.maximum(final_prices - min_prices, 0)
        else:
            max_prices = np.max(paths, axis=1)
            payoffs = np.maximum(max_prices - final_prices, 0)
        discount = np.exp(-self.r * self.T)
        price = discount * np.mean(payoffs)
        std_error = discount * np.std(payoffs) / np.sqrt(self.n_simulations)
        return float(price), float(std_error)

    def barrier_option_price(
        self,
        option_type="call",
        barrier_type="down-and-out",
        barrier_level=None,
    ):
        if barrier_level is None:
            barrier_level = (
                self.S * 0.9 if "down" in barrier_type else self.S * 1.1
            )
        paths = self._generate_paths()
        final_prices = paths[:, -1]
        if "down" in barrier_type:
            barrier_hit = np.any(paths <= barrier_level, axis=1)
        else:
            barrier_hit = np.any(paths >= barrier_level, axis=1)
        if option_type.lower() == "call":
            base_payoffs = np.maximum(final_prices - self.K, 0)
        else:
            base_payoffs = np.maximum(self.K - final_prices, 0)
        if "out" in barrier_type:
            payoffs = np.where(barrier_hit, 0, base_payoffs)
        else:
            payoffs = np.where(barrier_hit, base_payoffs, 0)
        discount = np.exp(-self.r * self.T)
        price = discount * np.mean(payoffs)
        std_error = discount * np.std(payoffs) / np.sqrt(self.n_simulations)
        return float(price), float(std_error), float(barrier_level)

    def get_results(self, option_type="call"):
        n_steps_calc = max(min(int(self.T * 252), 252), 21)
        self.n_steps = n_steps_calc
        self.dt = self.T / n_steps_calc

        european_price, european_se = self.european_option_price(option_type)
        asian_arith_price, asian_arith_se = self.asian_option_price(
            option_type, "arithmetic"
        )
        asian_geo_price, asian_geo_se = self.asian_option_price(
            option_type, "geometric"
        )
        lookback_price, lookback_se = self.lookback_option_price(option_type)
        barrier_type = "down-and-out" if option_type == "call" else "up-and-out"
        barrier_price, barrier_se, barrier_level = self.barrier_option_price(
            option_type, barrier_type
        )

        return {
            "simulations": self.n_simulations,
            "time_steps": self.n_steps,
            "european": {"price": european_price, "std_error": european_se},
            "asian_arithmetic": {
                "price": asian_arith_price,
                "std_error": asian_arith_se,
            },
            "asian_geometric": {
                "price": asian_geo_price,
                "std_error": asian_geo_se,
            },
            "lookback": {"price": lookback_price, "std_error": lookback_se},
            "barrier": {
                "price": barrier_price,
                "std_error": barrier_se,
                "barrier_type": barrier_type,
                "barrier_level": barrier_level,
            },
        }


class BinomialModel:
    """
    Cox-Ross-Rubinstein Binomial Tree model.

    Supports both European and American option pricing
    with early exercise valuation.
    """

    def __init__(self, S, K, T, r, sigma, q=0, n_steps=500):
        self.S = S
        self.K = K
        self.T = max(T, 1e-10)
        self.r = r
        self.sigma = max(sigma, 1e-10)
        self.q = q
        self.n_steps = n_steps
        self.dt = self.T / n_steps
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp((r - q) * self.dt) - self.d) / (self.u - self.d)
        self.discount = np.exp(-r * self.dt)

    def _build_terminal_stock_prices(self):
        n = self.n_steps
        return self.S * (self.u ** np.arange(n, -1, -1)) * (
            self.d ** np.arange(0, n + 1)
        )

    def european_option_price(self, option_type="call"):
        n = self.n_steps
        stock_prices = self._build_terminal_stock_prices()
        if option_type.lower() == "call":
            option_values = np.maximum(stock_prices - self.K, 0)
        else:
            option_values = np.maximum(self.K - stock_prices, 0)
        for i in range(n - 1, -1, -1):
            option_values = self.discount * (
                self.p * option_values[:-1] + (1 - self.p) * option_values[1:]
            )
        return float(option_values[0])

    def american_option_price(self, option_type="call"):
        n = self.n_steps
        stock_tree = np.zeros((n + 1, n + 1))
        stock_tree[0, 0] = self.S
        for i in range(1, n + 1):
            stock_tree[0:i, i] = stock_tree[0:i, i - 1] * self.u
            stock_tree[i, i] = stock_tree[i - 1, i - 1] * self.d
        option_tree = np.zeros((n + 1, n + 1))
        if option_type.lower() == "call":
            option_tree[:, n] = np.maximum(stock_tree[:, n] - self.K, 0)
        else:
            option_tree[:, n] = np.maximum(self.K - stock_tree[:, n], 0)
        early_exercise_count = 0
        for i in range(n - 1, -1, -1):
            continuation = self.discount * (
                self.p * option_tree[0 : i + 1, i + 1]
                + (1 - self.p) * option_tree[1 : i + 2, i + 1]
            )
            if option_type.lower() == "call":
                exercise = np.maximum(stock_tree[0 : i + 1, i] - self.K, 0)
            else:
                exercise = np.maximum(self.K - stock_tree[0 : i + 1, i], 0)
            early_exercise_count += int(np.sum(exercise > continuation))
            option_tree[0 : i + 1, i] = np.maximum(continuation, exercise)
        return float(option_tree[0, 0]), early_exercise_count

    def calculate_greeks(self, option_type="call", american=True):
        if american:
            price_func = lambda m: m.american_option_price(option_type)[0]
        else:
            price_func = lambda m: m.european_option_price(option_type)
        base_price = price_func(self)
        dS = self.S * 0.01
        model_up = BinomialModel(
            self.S + dS, self.K, self.T, self.r, self.sigma, self.q, self.n_steps
        )
        model_down = BinomialModel(
            self.S - dS, self.K, self.T, self.r, self.sigma, self.q, self.n_steps
        )
        delta = (price_func(model_up) - price_func(model_down)) / (2 * dS)
        gamma = (price_func(model_up) - 2 * base_price + price_func(model_down)) / (
            dS**2
        )
        if self.T > 1 / 365:
            dT = 1 / 365
            model_theta = BinomialModel(
                self.S,
                self.K,
                self.T - dT,
                self.r,
                self.sigma,
                self.q,
                self.n_steps,
            )
            theta = price_func(model_theta) - base_price
        else:
            theta = 0
        d_sigma = 0.01
        model_vega_up = BinomialModel(
            self.S,
            self.K,
            self.T,
            self.r,
            self.sigma + d_sigma,
            self.q,
            self.n_steps,
        )
        model_vega_down = BinomialModel(
            self.S,
            self.K,
            self.T,
            self.r,
            self.sigma - d_sigma,
            self.q,
            self.n_steps,
        )
        vega = (price_func(model_vega_up) - price_func(model_vega_down)) / 2
        return {
            "delta": float(delta),
            "gamma": float(gamma),
            "theta": float(theta),
            "vega": float(vega),
        }

    def get_results(self, option_type="call"):
        european_price = self.european_option_price(option_type)
        american_price, early_exercise_nodes = self.american_option_price(option_type)
        early_exercise_premium = american_price - european_price
        greeks = self.calculate_greeks(option_type, american=True)
        return {
            "tree_steps": self.n_steps,
            "up_factor": float(self.u),
            "down_factor": float(self.d),
            "risk_neutral_prob": float(self.p),
            "european_price": european_price,
            "american_price": american_price,
            "early_exercise_premium": early_exercise_premium,
            "early_exercise_nodes": early_exercise_nodes,
            "greeks": greeks,
        }
