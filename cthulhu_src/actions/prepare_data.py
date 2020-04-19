#!/usr/bin/env python
import ccxt
"""
    Prepare data about prices
"""

DEFAULT_EXCHANGERS_LIST = ["binance", "yobit"]


def get_data(log, exchanger: str):
    log.info(f"Start getting data from {exchanger}...")

    if exchanger not in ccxt.exchanges:
        log.critical(f"Not found exchanger {exchanger} in ccxt")
        return 1






def run(ctx, exchangers: list = DEFAULT_EXCHANGERS_LIST):
    """

    :param ctx: click context object
    :return:
    """
    log = ctx.obj["logger"]
    log.info(f"Start prepare data...")
    for exchanger in exchangers:
        get_data(log, exchanger)
