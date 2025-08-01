import click
from cthulhu_src.actions.forecast_backtest import run as run_cmd


@click.command()
@click.option("--prices", required=True, help="Comma separated price list")
@click.option("--horizon", default=5, type=int, help="Forecast horizon")
@click.option("--lookback", default=60, type=int, help="Lookback window")
@click.option(
    "--minutes-back",
    default=120,
    type=int,
    help="How many minutes ago to simulate the trade",
)
@click.pass_context
def forecast_backtest(
    ctx, prices: str, horizon: int, lookback: int, minutes_back: int
) -> None:
    """Check trade profitability ``minutes_back`` minutes in the past."""
    run_cmd(ctx, prices, horizon, lookback, minutes_back)
