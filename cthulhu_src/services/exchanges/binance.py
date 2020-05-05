from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class Binance(BaseExchange):
    name = 'binance'
    opts = {
        # 'enableRateLimit': True,
        'rateLimit': 500,
    }
    limit = 100
