"""Hollaex exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Hollaex(BatchingExchange):
    """Exchange adapter for Hollaex."""

    name = "hollaex"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 200
