from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Order:
    __slots__ = ["price", "amount"]
    price: float
    amount: float


TradeBook = List[Order]
NodeID = int
AdjacencyList = List[Dict[NodeID, TradeBook]]


@dataclass
class Pair:
    __slots__ = ["currency_from", "currency_to", "trade_book"]
    currency_from: str
    currency_to: str
    trade_book: TradeBook
