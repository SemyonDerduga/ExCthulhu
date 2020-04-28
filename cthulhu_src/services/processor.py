import itertools
from concurrent.futures.process import ProcessPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Optional

from cthulhu_src.services.pair import Trade


@dataclass
class Task:
    adj_list: List[Dict[int, List[Trade]]]
    start_node: int
    finish_node: int
    max_depth: int
    start_amount: float


def calc_price(initial_amount: float, current_trade_book: List[Trade]) -> Optional[float]:
    assert initial_amount
    assert current_trade_book
    currency_from_amount = 0
    currency_to_amount = 0

    for order in current_trade_book:
        if order.amount > (initial_amount - currency_from_amount):
            currency_to_amount += (initial_amount - currency_from_amount) * order.price
            currency_from_amount += initial_amount - currency_from_amount
            break
        else:
            currency_from_amount += order.amount
            currency_to_amount += order.amount * order.price

    if currency_from_amount != initial_amount:
        return None

    return currency_to_amount


def find_paths_worker(task: Task):
    path = [task.finish_node, task.start_node]
    seen = {task.finish_node, task.start_node}
    result = []

    def dfs(current_node: int, amount: float):
        if len(path) <= task.max_depth - 1:
            if task.finish_node in task.adj_list[current_node]:
                final_calculated_price = calc_price(amount, task.adj_list[current_node][task.finish_node])
                if final_calculated_price is not None and final_calculated_price > task.start_amount:
                    result.append((final_calculated_price, path.copy() + [task.finish_node]))
            if len(path) == task.max_depth - 1:
                return

        for node, trade_book in task.adj_list[current_node].items():
            if node not in seen:
                path.append(node)
                seen.add(node)

                next_price = calc_price(amount, trade_book)
                if next_price is not None:
                    dfs(node, calc_price(amount, trade_book))

                seen.remove(node)
                path.pop()

        return

    dfs(task.start_node, calc_price(task.start_amount, task.adj_list[task.finish_node][task.start_node]))
    return result


# max_depth includes start element
# example: max_depth:5 -> [0, 1, 2, 3, 0]
def find_paths(adj_list: List[Dict[int, List[Trade]]],
               start: int = 0, max_depth: int = 5, amount: float = 1):
    worker_tasks = [
        Task(adj_list=adj_list,
             start_node=transition,
             finish_node=start,
             max_depth=max_depth,
             start_amount=amount)
        for transition in adj_list[start].keys()
    ]
    with ProcessPoolExecutor() as executor:
        result = executor.map(find_paths_worker, worker_tasks)
    return list(itertools.chain(*result))
