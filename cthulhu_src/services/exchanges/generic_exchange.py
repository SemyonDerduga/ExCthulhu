"""Fallback exchange implementation for unknown names."""

from typing import Sequence

from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class GenericExchange(BaseExchange):
    """Exchange wrapper for exchanges not explicitly supported."""

    def __init__(self, name: str, proxies: Sequence[str]) -> None:
        self.name = name
        super().__init__(proxies)
