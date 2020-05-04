import asyncio
import logging
import sqlite3
from typing import List

from proxybroker import Broker, Proxy

logger = logging.getLogger('excthulhu')


class ProxyManager:
    def __init__(self, db_path, active_count=25, pool_size=100):
        self._change_proxy_lock = asyncio.Lock()
        self._pool_size = pool_size
        self._active_proxy_count = active_count
        self._db_conn = sqlite3.connect(db_path)
        self._db_cursor = self._db_conn.cursor()
        self._db_cursor.execute("""
            create table if not exists proxies (
                id integer primary key autoincrement,
                url text unique
            )
        """)

    async def ensure_pool(self):
        self._db_cursor.execute('select count(id) from proxies')
        table_size = self._db_cursor.fetchone()[0]
        if table_size < self._pool_size:
            await self.fetch_proxies(self._pool_size - table_size)

    def get_active_proxies(self) -> List[str]:
        self._db_cursor.execute("""
            select url from proxies
            order by id
            limit ?
        """, (self._active_proxy_count,))
        return [
            proxy[0]
            for proxy in self._db_cursor.fetchall()
        ]

    async def change_proxy(self, addr: str) -> str:
        logger.info(f'changing invalid proxy: {addr}...')
        self._db_cursor.execute("""
            select id, url from proxies
            where url = ?
        """, (addr,))
        dead_proxy = self._db_cursor.fetchone()
        if dead_proxy is not None:
            self._db_cursor.execute("""
                delete from proxies
                where id = ?
            """, (dead_proxy[0],))
            self._db_conn.commit()

            new_proxy = await self.fetch_proxies(1)
            return new_proxy[0]

        # get last active proxy, because it is the freshest
        self._db_cursor.execute("""
            select url from proxies
            order by id
            limit 1 offset ?
        """, (self._active_proxy_count - 1,))
        return self._db_cursor.fetchone()[0]

    async def fetch_proxies(self, count=1) -> List[str]:
        proxy_queue = asyncio.Queue(maxsize=2)
        broker = Broker(proxy_queue)
        broker_task = asyncio.create_task(broker.find(types=['HTTPS']))

        proxies = []
        for _ in range(count):
            while True:
                proxy: Proxy = await proxy_queue.get()
                proxy_url = f'http://{proxy.host}:{proxy.port}'

                try:
                    self._db_cursor.execute('insert into proxies(url) values (?)', (proxy_url,))
                    self._db_conn.commit()
                    proxies.append(proxy_url)

                    broker_task.cancel()
                    await broker_task
                    return proxies
                except sqlite3.IntegrityError as e:
                    logger.info(e)
