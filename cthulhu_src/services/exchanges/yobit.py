import logging
from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange

log = logging.getLogger('excthulhu')


class Yobit(BatchingExchange):
    name = 'yobit'
    opts = {
        'enableRateLimit': True,
        'rateLimit': 620,  # 600
    }
    limit = 2000

    max_batch_size = 20
