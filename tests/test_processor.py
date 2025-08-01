from cthulhu_src.services.processor import calc_price, find_paths_worker, Task
from cthulhu_src.services.arbitrage import find_paths_bellman_ford
from cthulhu_src.services.pair import Order


def test_calc_price_enough_first_order():
    book = [Order(price=2, amount=5)]
    assert calc_price(3, book) == 6


def test_calc_price_multiple_orders():
    book = [Order(price=2, amount=2), Order(price=1.5, amount=3)]
    # first order has amount 2 -> 2*2=4, remain 1 -> 1*1.5=1.5 => total 5.5
    assert calc_price(3, book) == 5.5


def test_calc_price_not_enough():
    book = [Order(price=1, amount=1)]
    assert calc_price(2, book) is None


def test_find_paths_worker_simple_profit():
    # adjacency list for two nodes 0 and 1
    adj_list = [{1: [Order(price=2, amount=10)]}, {0: [Order(price=0.6, amount=10)]}]
    task = Task(
        current_node=0,
        second_node=1,
        finish_node=0,
        start_amount=1.0,
        current_amount=1.0,
        max_depth=3,
        prune_ratio=0.0,
    )
    result = find_paths_worker(adj_list, task)
    assert result == [[(0, 1.0), (1, 2.0), (0, 1.2)]]


def test_find_paths_worker_insufficient_depth():
    adj_list = [{1: [Order(price=2, amount=10)]}, {0: [Order(price=0.6, amount=10)]}]
    task = Task(0, 1, 0, 1.0, 1.0, 2, 0.0)
    assert find_paths_worker(adj_list, task) == []


def test_bellman_ford_simple_cycle():
    adj_list = [{1: [Order(price=2, amount=10)]}, {0: [Order(price=0.6, amount=10)]}]
    result = find_paths_bellman_ford(adj_list, 0, 1.0)
    assert result[0][-1][1] > 1.0
