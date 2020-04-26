import itertools
from concurrent.futures.process import ProcessPoolExecutor
from dataclasses import dataclass
from typing import List, Dict

from cthulhu_src.services.pair import Trade


@dataclass
class Task:
    adj_list: List[Dict[int, List[Trade]]]
    start_node: int
    finish_node: int
    max_len: int
    amount: float


def find_paths_worker(task: Task):
    path = [task.finish_node, task.start_node]
    seen = {task.finish_node, task.start_node}
    result = []

    def dfs(current_node: int):
        if len(path) == task.max_len - 1:
            if task.finish_node in task.adj_list[current_node]:
                result.append(path.copy() + [task.finish_node])
            return

        for node, trade_book in task.adj_list[current_node].items():
            if node not in seen:
                path.append(node)
                seen.add(node)

                dfs(node)

                seen.remove(node)
                path.pop()

    dfs(task.start_node)
    return result


# max_len includes start element
# example: max_len:5 -> [0, 1, 2, 3, 0]
def find_paths(adj_list: List[Dict[int, List[Trade]]],
               start: int = 0, max_len: int = 5, amount: float = 1):
    worker_tasks = [
        Task(adj_list=adj_list,
             start_node=transition,
             finish_node=start,
             max_len=max_len,
             amount=amount)
        for transition in adj_list[start].keys()
    ]
    with ProcessPoolExecutor() as executor:
        result = executor.map(find_paths_worker, worker_tasks)
    return list(itertools.chain(*result))
