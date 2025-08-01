"""Oceanex exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Oceanex(BatchingExchange):
    """Exchange adapter for Oceanex."""

    name = "oceanex"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 200
