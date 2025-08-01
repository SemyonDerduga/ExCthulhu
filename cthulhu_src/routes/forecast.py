import click
from cthulhu_src.actions.forecast import run as run_cmd


@click.command()
@click.option("--prices", required=True, help="Comma separated price list")
@click.option(
    "--horizons",
    default="1,5,15,60",
    help="Comma separated forecast horizons",
)
@click.option("--lookback", default=60, type=int, help="Lookback window")
@click.option(
    "--methods",
    default="mean",
    help="Comma separated prediction methods (mean, median, ema)",
)
@click.pass_context
def forecast(ctx, prices: str, horizons: str, lookback: int, methods: str) -> None:
    """Calculate naive forecasts for given prices."""
    run_cmd(ctx, prices, horizons, lookback, methods)
