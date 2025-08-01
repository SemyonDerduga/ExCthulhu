from cthulhu_src.services.forecast import ForecastService


def run(ctx, prices: str, horizon: int, lookback: int, minutes_back: int) -> None:
    price_list = [float(p) for p in prices.split(",") if p]
    svc = ForecastService(lookback=lookback)
    success = svc.backtest(price_list, horizon, minutes_back=minutes_back)
    print("profitable" if success else "not profitable")
