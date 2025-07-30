from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Tidex(BatchingExchange):
    name = "tidex"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 400
