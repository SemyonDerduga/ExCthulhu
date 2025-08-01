"""Data structures used across ExCthulhu services."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Order:
    """Represents a single order in the order book."""

    __slots__ = ["price", "amount"]

    price: float
    amount: float


TradeBook = List[Order]
NodeID = int
AdjacencyList = List[Dict[NodeID, TradeBook]]


@dataclass
class Pair:
    """Exchange pair together with its order book."""

    __slots__ = ["currency_from", "currency_to", "trade_book"]

    currency_from: str
    currency_to: str
    trade_book: TradeBook
