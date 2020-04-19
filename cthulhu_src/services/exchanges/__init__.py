from .base_exchange import BaseExchange
from .batching_exchange import BatchingExchange
from .generic_exchange import GenericExchange
from .binance import Binance
from .dsx import Dsx
from .exmo import Exmo
from .hollaex import Hollaex
from .oceanex import Oceanex
from .poloniex import Poloniex
from .tidex import Tidex
from .upbit import Upbit
from .yobit import Yobit

__all__ = ['BaseExchange', 'BatchingExchange', 'Binance', 'Dsx', 'Exmo',
           'Hollaex', 'Oceanex', 'Poloniex', 'Tidex', 'Upbit', 'Yobit']

exchanges = {
    'binance': Binance,
    'dsx': Dsx,
    'exmo': Exmo,
    'hollaex': Hollaex,
    'oceanex': Oceanex,
    'poloniex': Poloniex,
    'tidex': Tidex,
    'upbit': Upbit,
    'yobit': Yobit,
}


def get_exchange_by_name(exchange_name):
    if exchange_name in exchanges:
        return exchanges[exchange_name]()
    else:
        return GenericExchange(exchange_name)
