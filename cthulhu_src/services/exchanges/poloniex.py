from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Poloniex(BatchingExchange):
    name = 'poloniex'
    opts = {
        'enableRateLimit': True,
    }

    max_batch_size = 200
