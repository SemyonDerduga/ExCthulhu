from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


class Exmo(BatchingExchange):
    name = 'exmo'
    opts = {
        'enableRateLimit': True,
        'rateLimit': 110,  # 100
    }

    max_batch_size = 200
