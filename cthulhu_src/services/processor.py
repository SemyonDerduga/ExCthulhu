import logging
import os
import itertools
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional, Tuple
from multiprocessing import Process, Queue
from time import time

from tqdm import tqdm

from bisect import bisect_left
from cthulhu_src.services.pair import AdjacencyList, NodeID, TradeBook

logger = logging.getLogger("excthulhu")


@dataclass
class Task:
    current_node: NodeID  # node where algorithm start
    second_node: NodeID  # node where starts dfs
    finish_node: NodeID  # node where algorithm going to

    start_amount: float  # to compare start and finish amount
    current_amount: float  # amount at the moment when algorithm starts

    max_depth: int  # max depth to search
    prune_ratio: float = 0.0  # branch pruning ratio


Step = Tuple[NodeID, float]
Path = List[Step]


_cumulative_cache: dict[int, tuple[list[float], list[float]]] = {}
_price_cache: dict[tuple[int, float], Optional[float]] = {}


def calc_price(trading_amount: float, current_trade_book: TradeBook) -> Optional[float]:
    """Calculate resulting currency amount using binary search and caching."""
    cache_key = (id(current_trade_book), trading_amount)
    if cache_key in _price_cache:
        return _price_cache[cache_key]

    if not current_trade_book:
        _price_cache[cache_key] = None
        return None

    data = _cumulative_cache.get(id(current_trade_book))
    if data is None:
        amounts, costs = [], []
        total_amount = 0.0
        total_cost = 0.0
        for order in current_trade_book:
            total_amount += order.amount
            total_cost += order.amount * order.price
            amounts.append(total_amount)
            costs.append(total_cost)
        data = (amounts, costs)
        _cumulative_cache[id(current_trade_book)] = data

    amounts, costs = data
    if trading_amount > amounts[-1]:
        _price_cache[cache_key] = None
        return None

    idx = bisect_left(amounts, trading_amount)
    prev_amount = amounts[idx - 1] if idx > 0 else 0.0
    prev_cost = costs[idx - 1] if idx > 0 else 0.0
    remaining = trading_amount - prev_amount
    result = prev_cost + remaining * current_trade_book[idx].price

    _price_cache[cache_key] = result
    return result


def find_paths_worker(adj_list: AdjacencyList, task: Task) -> List[Path]:
    if task.max_depth < 3:
        return []

    second_amount = calc_price(
        task.current_amount, adj_list[task.current_node][task.second_node]
    )
    if second_amount is None:
        return []

    path = [
        (task.current_node, task.current_amount),
        (task.second_node, second_amount),
    ]
    seen = {task.current_node, task.second_node}
    result = []

    def dfs(current_node: NodeID, amount: float):
        if task.finish_node in adj_list[current_node]:
            final_calculated_price = calc_price(
                amount, adj_list[current_node][task.finish_node]
            )
            if (
                final_calculated_price is not None
                and final_calculated_price > task.start_amount
            ):
                result.append(
                    path.copy() + [(task.finish_node, final_calculated_price)]
                )

        if len(path) == task.max_depth - 1:
            return

        for node, trade_book in adj_list[current_node].items():
            if node not in seen:
                next_price = calc_price(amount, trade_book)
                if next_price is None:
                    continue
                if (
                    task.prune_ratio > 0
                    and next_price <= task.start_amount * task.prune_ratio
                ):
                    continue

                path.append((node, next_price))
                seen.add(node)

                dfs(node, next_price)

                seen.remove(node)
                path.pop()

        return

    dfs(task.second_node, second_amount)
    return result


@contextmanager
def workers(*args, num_workers: int = None, **kwargs):
    if num_workers is None:
        num_workers = os.cpu_count()
    processes = [Process(*args, **kwargs) for _ in range(num_workers)]

    begin = time()
    for process in processes:
        process.start()

    try:
        yield
        end = time()
        delta_ms = (end - begin) * 1000
        logger.info(f"Processed in {delta_ms} ms")
    finally:
        for process in processes:
            process.terminate()
            process.join()
            process.close()


# max_depth includes start element
# example: max_depth=5 -> [0, 1, 2, 3, 0]
def find_paths(
    adj_list: AdjacencyList,
    start_node: NodeID,
    start_amount: float,
    current_node: Optional[NodeID] = None,
    current_amount: Optional[int] = None,
    max_depth: int = 5,
    prune_ratio: float = 0.0,
    num_workers: int | None = None,
) -> List[Path]:
    if current_node is not None and current_amount is not None:
        worker_tasks = [
            Task(
                current_node=current_node,
                second_node=second_node,
                finish_node=start_node,
                start_amount=start_amount,
                current_amount=current_amount,
                max_depth=max_depth,
                prune_ratio=prune_ratio,
            )
            for second_node in adj_list[current_node].keys()
        ]
    else:
        worker_tasks = [
            Task(
                current_node=start_node,
                second_node=second_node,
                finish_node=start_node,
                start_amount=start_amount,
                current_amount=start_amount,
                max_depth=max_depth,
                prune_ratio=prune_ratio,
            )
            for second_node in adj_list[start_node].keys()
        ]

    task_queue = Queue()
    for task in worker_tasks:
        task_queue.put(task)

    result_queue = Queue()
    with workers(
        target=worker,
        args=(adj_list, task_queue, result_queue),
        num_workers=num_workers,
    ):
        results = [
            result_queue.get()
            for _ in tqdm(range(len(worker_tasks)), unit="task", dynamic_ncols=True)
        ]
    return list(itertools.chain(*results))


def worker(adj_list: AdjacencyList, task_queue: Queue, result_queue: Queue):
    while True:
        task = task_queue.get()
        result = find_paths_worker(adj_list, task)
        result_queue.put(result)
