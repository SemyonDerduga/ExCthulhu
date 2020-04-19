from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Upbit(BatchingExchange):
    name = 'upbit'
    opts = {
        'enableRateLimit': True,
    }

    max_batch_size = 400
