import logging
import os
import itertools
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional, Tuple
from multiprocessing import Process, Queue
from time import time

from tqdm import tqdm

from cthulhu_src.services.pair import AdjacencyList, NodeID, TradeBook

logger = logging.getLogger('excthulhu')


@dataclass
class Task:
    current_node: NodeID  # node where algorithm start
    second_node: NodeID  # node where starts dfs
    finish_node: NodeID  # node where algorithm going to

    start_amount: float  # to compare start and finish amount
    current_amount: float  # amount at the moment when algorithm starts

    max_depth: int  # max depth to search


Step = Tuple[NodeID, float]
Path = List[Step]


def calc_price(trading_amount: float, current_trade_book: TradeBook) -> Optional[float]:
    target_currency_amount = 0

    for order in current_trade_book:
        if order.amount >= trading_amount:
            target_currency_amount += trading_amount * order.price
            return target_currency_amount

        trading_amount -= order.amount
        target_currency_amount += order.amount * order.price

    return None


def find_paths_worker(adj_list: AdjacencyList, task: Task) -> List[Path]:
    if task.max_depth < 3:
        return []

    second_amount = calc_price(task.current_amount, adj_list[task.current_node][task.second_node])
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
            final_calculated_price = calc_price(amount, adj_list[current_node][task.finish_node])
            if final_calculated_price is not None and final_calculated_price > task.start_amount:
                result.append(path.copy() + [(task.finish_node, final_calculated_price)])

        if len(path) == task.max_depth - 1:
            return

        for node, trade_book in adj_list[current_node].items():
            if node not in seen:
                next_price = calc_price(amount, trade_book)
                if next_price is None:
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
def workers(*args, **kwargs):
    processes = [
        Process(*args, **kwargs)
        for _ in range(os.cpu_count())
    ]

    begin = time()
    for process in processes:
        process.start()

    try:
        yield
        end = time()
        delta_ms = (end - begin) * 1000
        logger.info(f'Processed in {delta_ms} ms')
    finally:
        for process in processes:
            process.terminate()
            process.join()
            process.close()


# max_depth includes start element
# example: max_depth=5 -> [0, 1, 2, 3, 0]
def find_paths(adj_list: AdjacencyList,
               start_node: NodeID, start_amount: float,
               current_node: Optional[NodeID] = None, current_amount: Optional[int] = None,
               max_depth: int = 5) -> List[Path]:
    if current_node is not None and current_amount is not None:
        worker_tasks = [
            Task(current_node=current_node,
                 second_node=second_node,
                 finish_node=start_node,
                 start_amount=start_amount,
                 current_amount=current_amount,
                 max_depth=max_depth)
            for second_node in adj_list[current_node].keys()
        ]
    else:
        worker_tasks = [
            Task(current_node=start_node,
                 second_node=second_node,
                 finish_node=start_node,
                 start_amount=start_amount,
                 current_amount=start_amount,
                 max_depth=max_depth)
            for second_node in adj_list[start_node].keys()
        ]

    task_queue = Queue()
    for task in worker_tasks:
        task_queue.put(task)

    result_queue = Queue()
    with workers(target=worker, args=(adj_list, task_queue, result_queue)):
        results = [
            result_queue.get()
            for _ in tqdm(range(len(worker_tasks)), unit='task', dynamic_ncols=True)
        ]
    return list(itertools.chain(*results))


def worker(adj_list: AdjacencyList, task_queue: Queue, result_queue: Queue):
    while True:
        task = task_queue.get()
        result = find_paths_worker(adj_list, task)
        result_queue.put(result)
