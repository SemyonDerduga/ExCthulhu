from dataclasses import dataclass
from typing import List


@dataclass
class Order:
    __slots__ = ['price', 'amount']
    price: float
    amount: float


@dataclass
class Pair:
    __slots__ = ['currency_from', 'currency_to', 'trade_book']
    currency_from: str
    currency_to: str
    trade_book: List[Order]
