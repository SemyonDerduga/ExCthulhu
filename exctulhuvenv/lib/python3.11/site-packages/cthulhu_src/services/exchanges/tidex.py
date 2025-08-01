"""Tidex exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Tidex(BatchingExchange):
    """Exchange adapter for Tidex."""

    name = "tidex"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 400
