import os
import itertools
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from multiprocessing import Process, Queue

from cthulhu_src.services.pair import Order


@dataclass
class Task:
    current_node: int  # node where algorithm start
    second_node: int  # node where starts dfs
    finish_node: int  # node where algorithm going to

    start_amount: float  # to compare start and finish amount
    current_amount: float  # amount at the moment when algorithm starts

    max_depth: int  # max depth to search


def calc_price(trading_amount: float, current_trade_book: List[Order]) -> Optional[float]:
    target_currency_amount = 0

    for order in current_trade_book:
        if order.amount >= trading_amount:
            target_currency_amount += trading_amount * order.price
            return target_currency_amount

        trading_amount -= order.amount
        target_currency_amount += order.amount * order.price

    return None


def find_paths_worker(adj_list: List[Dict[int, List[Order]]], task: Task) -> List[Tuple[int, float]]:
    second_amount = calc_price(task.current_amount, adj_list[task.current_node][task.second_node])
    if second_amount is None:
        return []

    path = [
        (task.current_node, task.current_amount),
        (task.second_node, second_amount),
    ]
    seen = {task.current_node, task.second_node}
    result = []

    def dfs(current_node: int, amount: float):
        if len(path) <= task.max_depth - 1:
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


# max_depth includes start element
# example: max_depth=5 -> [0, 1, 2, 3, 0]
def find_paths(adj_list: List[Dict[int, List[Order]]],
               start_node: int, start_amount: float,
               current_node: Optional[int] = None, current_amount: Optional[int] = None,
               max_depth: int = 5) -> List[Tuple[int, float]]:
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
    processes = [
        Process(target=worker, args=(adj_list, task_queue, result_queue))
        for _ in range(os.cpu_count())
    ]

    for process in processes:
        process.start()

    results = []
    for i in range(len(worker_tasks)):
        results.append(result_queue.get())

    for process in processes:
        process.terminate()

    return list(itertools.chain(*results))


def worker(adj_list: List[Dict[int, List[Order]]], task_queue: Queue, result_queue: Queue):
    while True:
        task = task_queue.get()
        if task is None:
            break
        result = find_paths_worker(adj_list, task)
        result_queue.put_nowait(result)
