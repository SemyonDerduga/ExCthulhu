from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Oceanex(BatchingExchange):
    name = "oceanex"
    opts = {
        "enableRateLimit": True,
    }

    max_batch_size = 200
