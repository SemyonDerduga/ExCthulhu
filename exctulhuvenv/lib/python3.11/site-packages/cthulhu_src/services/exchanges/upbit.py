"""Upbit exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Upbit(BatchingExchange):
    """Exchange adapter for Upbit."""

    name = "upbit"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 400
