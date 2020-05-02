import os
import itertools
from dataclasses import dataclass
from typing import List, Dict, Optional
from multiprocessing import Process, Queue

from cthulhu_src.services.pair import Order


@dataclass
class Task:
    second_node: int
    current_node: int
    finish_node: int
    max_depth: int
    start_amount: float
    current_amount: float


def calc_price(trading_amount: float, current_trade_book: List[Order]) -> Optional[float]:
    target_currency_amount = 0

    for order in current_trade_book:
        if order.amount >= trading_amount:
            target_currency_amount += trading_amount * order.price
            return target_currency_amount

        trading_amount -= order.amount
        target_currency_amount += order.amount * order.price

    return None


def find_paths_worker(adj_list: List[Dict[int, List[Order]]], task: Task):
    first_transition_amount = calc_price(task.current_amount, adj_list[task.current_node][task.second_node])
    if first_transition_amount is None:
        return []

    path = [
        (task.current_node, task.current_amount),
        (task.second_node, first_transition_amount),
    ]
    seen = {task.finish_node, task.second_node}
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

    dfs(task.second_node, first_transition_amount)
    return result


# max_depth includes start element
# example: max_depth:5 -> [0, 1, 2, 3, 0]
def find_paths(adj_list: List[Dict[int, List[Order]]],
               start: int = 0, max_depth: int = 5, amount: float = 1, current_node=None, current_amount=None):
    if current_node and current_amount:
        worker_tasks = [
            Task(second_node=transition,
                 current_node=current_node,
                 finish_node=start,
                 max_depth=max_depth,
                 start_amount=amount,
                 current_amount=current_amount)
            for transition in adj_list[current_node].keys()
        ]
    else:
        worker_tasks = [
            Task(second_node=transition,
                 current_node=start,
                 finish_node=start,
                 max_depth=max_depth,
                 start_amount=amount,
                 current_amount=amount)
            for transition in adj_list[start].keys()
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
