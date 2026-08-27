"""
No-network sanity tests for the pricing models.

Every test here builds a model from literal parameters, so nothing in this file
touches yfinance, the network, or the Flask app. Run with:

    python -m unittest discover -s tests
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.pricing_models import BinomialModel, BlackScholesModel


class TestPutCallParity(unittest.TestCase):
    """C - P == S*exp(-qT) - K*exp(-rT) for European options."""

    CASES = [
        # (S, K, T, r, sigma, q)
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.0),
        (100.0, 120.0, 0.5, 0.03, 0.35, 0.02),
        (100.0, 80.0, 2.0, 0.05, 0.15, 0.04),
        (42.5, 40.0, 0.25, 0.01, 0.60, 0.0),
    ]

    def test_black_scholes_satisfies_put_call_parity(self):
        for S, K, T, r, sigma, q in self.CASES:
            with self.subTest(S=S, K=K, T=T, r=r, sigma=sigma, q=q):
                bs = BlackScholesModel(S, K, T, r, sigma, q)
                lhs = bs.call_price() - bs.put_price()
                rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
                # norm_cdf uses Hasting's approximation (~1e-7 absolute), and
                # parity subtracts two prices, so allow a few multiples of that.
                self.assertAlmostEqual(lhs, rhs, delta=1e-4 * max(1.0, S))

    def test_binomial_european_satisfies_put_call_parity(self):
        for S, K, T, r, sigma, q in self.CASES:
            with self.subTest(S=S, K=K, T=T, r=r, sigma=sigma, q=q):
                model = BinomialModel(S, K, T, r, sigma, q, n_steps=400)
                lhs = model.european_option_price("call") - model.european_option_price("put")
                rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
                self.assertAlmostEqual(lhs, rhs, delta=1e-6 * max(1.0, S))


class TestAmericanDominatesEuropean(unittest.TestCase):
    """An American option can be exercised early, so it is never worth less."""

    CASES = [
        # (S, K, T, r, sigma, q, option_type)
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.00, "put"),
        (100.0, 130.0, 1.0, 0.06, 0.25, 0.00, "put"),   # deep ITM put
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.08, "call"),  # q > r, early exercise
        (100.0, 70.0, 2.0, 0.04, 0.30, 0.06, "call"),   # deep ITM dividend call
        (100.0, 100.0, 0.5, 0.02, 0.40, 0.01, "put"),
    ]

    def test_american_price_is_at_least_european_price(self):
        for S, K, T, r, sigma, q, option_type in self.CASES:
            with self.subTest(S=S, K=K, T=T, r=r, sigma=sigma, q=q, type=option_type):
                model = BinomialModel(S, K, T, r, sigma, q, n_steps=300)
                european = model.european_option_price(option_type)
                american, _ = model.american_option_price(option_type)
                # Same lattice for both, so the inequality is exact up to
                # floating point noise -- no pricing-error tolerance needed.
                self.assertGreaterEqual(american, european - 1e-9)

    def test_early_exercise_premium_is_positive_when_exercise_is_optimal(self):
        # Deep in-the-money American put with a meaningful rate: waiting costs
        # interest on the strike, so early exercise must carry real value.
        model = BinomialModel(100.0, 150.0, 1.0, 0.08, 0.20, 0.0, n_steps=300)
        results = model.get_results("put")
        self.assertGreater(results["early_exercise_premium"], 0.0)
        self.assertGreater(results["early_exercise_nodes"], 0)


class TestZeroDividendPremium(unittest.TestCase):
    """
    With q = 0 it is never optimal to exercise an American call early, so its
    early exercise premium over the European call is zero (Merton, 1973).
    """

    CASES = [
        # (S, K, T, r, sigma)
        (100.0, 100.0, 1.0, 0.05, 0.20),
        (100.0, 60.0, 1.0, 0.05, 0.20),   # deep ITM
        (100.0, 140.0, 2.0, 0.07, 0.30),  # deep OTM, long dated
        (250.0, 250.0, 0.5, 0.03, 0.45),
    ]

    def test_american_call_has_no_early_exercise_premium_without_dividends(self):
        for S, K, T, r, sigma in self.CASES:
            with self.subTest(S=S, K=K, T=T, r=r, sigma=sigma):
                model = BinomialModel(S, K, T, r, sigma, q=0.0, n_steps=300)
                results = model.get_results("call")
                self.assertAlmostEqual(
                    results["early_exercise_premium"], 0.0, delta=1e-8 * max(1.0, S)
                )
                self.assertEqual(results["early_exercise_nodes"], 0)

    def test_zero_dividend_binomial_call_converges_to_black_scholes(self):
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        binomial = BinomialModel(S, K, T, r, sigma, q=0.0, n_steps=800)
        analytic = BlackScholesModel(S, K, T, r, sigma, q=0.0).call_price()
        self.assertAlmostEqual(binomial.european_option_price("call"), analytic, delta=0.05)


class TestRiskNeutralProbabilityGuard(unittest.TestCase):
    """The lattice must refuse parameters that break d < exp((r-q)dt) < u."""

    def test_valid_parameters_produce_a_probability_in_the_unit_interval(self):
        model = BinomialModel(100.0, 100.0, 1.0, 0.05, 0.20, 0.02, n_steps=200)
        self.assertGreater(model.p, 0.0)
        self.assertLess(model.p, 1.0)

    def test_percentage_scale_dividend_yield_is_rejected(self):
        # 4.4 is a dividend yield of 440% -- the shape of the old units bug,
        # which used to silently return an astronomically wrong price.
        with self.assertRaises(ValueError) as ctx:
            BinomialModel(100.0, 100.0, 1.0, 0.05, 0.20, 4.4, n_steps=50)
        self.assertIn("no-arbitrage", str(ctx.exception))


class TestDividendYieldUnits(unittest.TestCase):
    """
    yfinance hands back `dividendYield` as a percentage number; the models want
    a decimal fraction. Stub out the info dict so this stays offline.
    """

    def _yield_for(self, raw):
        from lib.market_data_fetcher import MarketDataFetcher

        fetcher = MarketDataFetcher("TEST")
        fetcher._info = {"dividendYield": raw}
        return fetcher.dividend_yield

    def test_percentage_is_converted_to_a_fraction(self):
        self.assertAlmostEqual(self._yield_for(0.53), 0.0053)
        self.assertAlmostEqual(self._yield_for(4.4), 0.044)

    def test_missing_or_implausible_values_fall_back_to_zero(self):
        for raw in (None, 0, "", float("nan"), -1.0, 250.0):
            with self.subTest(raw=raw):
                self.assertEqual(self._yield_for(raw), 0.0)


if __name__ == "__main__":
    unittest.main()
