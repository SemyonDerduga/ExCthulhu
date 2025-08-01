"""Binance exchange adapter."""

from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class Binance(BaseExchange):
    """ccxt-based adapter for Binance."""

    name = "binance"
    opts = {
        # 'enableRateLimit': True,
        # 'rateLimit': 500,
    }
    limit = 100
