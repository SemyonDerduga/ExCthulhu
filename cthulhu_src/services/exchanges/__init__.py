from .yobit import Yobit
from .binance import Binance
from .base_exchange import BaseExchange
from .generic_exchange import GenericExchange

__all__ = ['BaseExchange', 'Yobit', 'Binance']

exchanges = {
    'yobit': Yobit,
    'binance': Binance,
}


def get_exchange_by_name(exchange_name):
    if exchange_name in exchanges:
        return exchanges[exchange_name]()
    else:
        return GenericExchange(exchange_name)
