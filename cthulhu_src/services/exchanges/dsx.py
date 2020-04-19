from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange


# doesn't work
class Dsx(BatchingExchange):
    name = 'dsx'
    opts = {
        'enableRateLimit': True,
    }

    max_batch_size = 20
