from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class Yobit(BaseExchange):
    name = 'yobit'
    opts = {
        'enableRateLimit': True,
    }
