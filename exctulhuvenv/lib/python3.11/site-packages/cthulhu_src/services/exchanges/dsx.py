"""Dsx exchange adapter."""

from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


# doesn't work
class Dsx(BatchingExchange):
    """Exchange adapter for DSX."""

    name = "dsx"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 20
