from cthulhu_src.services.forecast import ForecastService


def run(ctx, prices: str, horizons: str, lookback: int, methods: str) -> None:
    price_list = [float(p) for p in prices.split(",") if p]
    horizon_list = [int(h) for h in horizons.split(",") if h]
    method_list = [m.strip() for m in methods.split(",") if m]
    service = ForecastService(lookback=lookback)
    results = service.predict_many(price_list, horizon_list, method_list)
    for method, forecasts in results.items():
        print(f"method: {method}")
        for fc in forecasts:
            print(
                f"  h={fc.h} mu={fc.mu:.6f} sigma={fc.sigma:.6f} q10={fc.q10:.6f} q50={fc.q50:.6f} q90={fc.q90:.6f}"
            )
