from typing import List

from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class GenericExchange(BaseExchange):
    def __init__(self, name: str, proxies: List[str]):
        self.name = name
        super().__init__(proxies)
