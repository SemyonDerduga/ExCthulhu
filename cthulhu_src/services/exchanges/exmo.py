"""Exmo exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Exmo(BatchingExchange):
    """Exchange adapter for Exmo."""

    name = "exmo"
    opts = {
        "enableRateLimit": True,
        "rateLimit": 110,  # 100
    }

    max_batch_size = 200
