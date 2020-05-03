import asyncio
from typing import List, Dict


class ProxyManager:
    def __init__(self, proxies: List[str]):
        self._active_proxies = proxies
        self._dead_proxy_old_indices: Dict[str, int] = dict()
        self._change_proxy_lock = asyncio.Lock()

    def get_active_proxies(self) -> List[str]:
        return self._active_proxies

    async def change_proxy(self, addr: str) -> str:
        if addr in self._dead_proxy_old_indices:
            dead_proxy_old_index = self._dead_proxy_old_indices[addr]
            return self._active_proxies[dead_proxy_old_index]

        if addr in self._active_proxies:
            async with self._change_proxy_lock:
                dead_proxy_index = self._active_proxies.index(addr)
                self._dead_proxy_old_indices[addr] = dead_proxy_index

                new_proxy = await self.fetch_proxy()
                self._active_proxies[dead_proxy_index] = new_proxy

                return new_proxy

        raise KeyError('proxy not found')

    async def fetch_proxy(self) -> str:
        raise NotImplementedError('fetch_proxy function not implemented yet')
