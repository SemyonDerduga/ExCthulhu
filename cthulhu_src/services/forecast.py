from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm


@dataclass
class Forecast:
    """Container for forecast statistics."""

    h: int
    mu: float
    sigma: float
    q10: float
    q50: float
    q90: float


class ForecastService:
    """Forecasting service using simple statistics or ARIMA model."""

    SUPPORTED_METHODS = ("mean", "median", "ema", "arima")

    def __init__(self, lookback: int = 60) -> None:
        self.lookback = lookback

    def predict(
        self, prices: Iterable[float], horizons: Iterable[int], method: str = "mean"
    ) -> List[Forecast]:
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"unknown method {method}")

        prices_list = list(prices)
        if not prices_list:
            raise ValueError("prices sequence is empty")
        max_h = max(horizons)
        required = self.lookback + max_h
        if len(prices_list) < required:
            raise ValueError("not enough price history for given lookback and horizon")

        log_prices = np.log(np.asarray(prices_list, dtype=float))
        returns = np.diff(log_prices)

        forecasts: List[Forecast] = []
        for h in horizons:
            window = returns[-(self.lookback + h - 1) :]
            r_h = window[-h:]

            if method == "mean":
                mu = float(np.mean(r_h))
            elif method == "median":
                mu = float(np.median(r_h))
            elif method == "ema":
                weights = np.exp(np.linspace(-1.0, 0.0, len(r_h)))
                weights /= weights.sum()
                mu = float(np.dot(weights, r_h))
            elif method == "arima":
                model = sm.tsa.ARIMA(window, order=(1, 0, 0)).fit()
                fc = model.get_forecast(steps=h)
                mu = float(np.sum(fc.predicted_mean))
                sigma = float(np.sqrt(np.sum(fc.var_pred_mean)))
                z10, z90 = norm.ppf([0.1, 0.9])
                q10 = mu + z10 * sigma
                q50 = mu
                q90 = mu + z90 * sigma
                forecasts.append(
                    Forecast(h=int(h), mu=mu, sigma=sigma, q10=q10, q50=q50, q90=q90)
                )
                continue

            sigma = float(np.std(r_h, ddof=1)) if len(r_h) > 1 else 0.0
            q10, q50, q90 = np.quantile(r_h, [0.1, 0.5, 0.9])

            forecasts.append(
                Forecast(
                    h=int(h),
                    mu=mu,
                    sigma=sigma,
                    q10=float(q10),
                    q50=float(q50),
                    q90=float(q90),
                )
            )
        return forecasts

    def predict_many(
        self,
        prices: Sequence[float],
        horizons: Sequence[int],
        methods: Sequence[str],
    ) -> Dict[str, List[Forecast]]:
        """Run several prediction methods and gather their results."""

        results: Dict[str, List[Forecast]] = {}
        for m in methods:
            results[m] = self.predict(prices, horizons, method=m)
        return results

    def backtest(
        self, prices: Iterable[float], horizon: int, minutes_back: int = 120
    ) -> bool:
        """Evaluate a trade placed ``minutes_back`` minutes ago.

        Parameters
        ----------
        prices:
            Sequence of historical prices ordered oldest to newest. Prices must
            contain the window used for training and the period to backtest.
        horizon:
            Forecast horizon in minutes for the simulated trade.
        minutes_back:
            How many minutes in the past to start the trade. By default two
            hours (120 minutes).
        """
        prices_list = list(prices)
        required = self.lookback + horizon + minutes_back
        if len(prices_list) < required:
            raise ValueError("not enough price history for backtest")

        start_idx = len(prices_list) - minutes_back
        forecast = self.predict(prices_list[:start_idx], [horizon])[0]
        if forecast.mu <= 0:
            return False
        log_ret = float(
            np.log(prices_list[start_idx + horizon] / prices_list[start_idx])
        )
        return log_ret > 0
