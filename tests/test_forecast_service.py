import math
import pytest
from cthulhu_src.services.forecast import ForecastService


def test_forecast_constant_returns():
    prices = [2**i for i in range(70)]
    svc = ForecastService(lookback=60)
    results = svc.predict(prices, [1, 5])
    assert len(results) == 2
    for res in results:
        assert math.isclose(res.mu, math.log(2), rel_tol=1e-9)
        assert math.isclose(res.sigma, 0.0, abs_tol=1e-12)
        assert math.isclose(res.q10, math.log(2), rel_tol=1e-9)
        assert math.isclose(res.q50, math.log(2), rel_tol=1e-9)
        assert math.isclose(res.q90, math.log(2), rel_tol=1e-9)


def test_forecast_not_enough():
    svc = ForecastService(lookback=10)
    with pytest.raises(ValueError):
        svc.predict([1, 2, 3], [1])


def test_backtest_minutes_back():
    prices = [2**i for i in range(200)]
    svc = ForecastService(lookback=60)
    assert svc.backtest(prices, horizon=5, minutes_back=120) is True


def test_predict_many():
    prices = [2**i for i in range(70)]
    svc = ForecastService(lookback=60)
    results = svc.predict_many(prices, [1, 5], ["mean", "ema", "arima"])
    assert set(results.keys()) == {"mean", "ema", "arima"}
    assert len(results["mean"]) == 2


def test_arima_constant_returns():
    prices = [2**i for i in range(70)]
    svc = ForecastService(lookback=60)
    res = svc.predict(prices, [1], method="arima")[0]
    assert math.isclose(res.mu, math.log(2), rel_tol=1e-2)
