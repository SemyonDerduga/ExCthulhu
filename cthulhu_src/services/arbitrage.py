"""Arbitrage search algorithms."""

from __future__ import annotations

import math
from typing import List

from .pair import AdjacencyList, NodeID
from .processor import calc_price, Path


def _build_edges(adj_list: AdjacencyList) -> List[tuple[int, int, float]]:
    edges: List[tuple[int, int, float]] = []
    for u, neighbours in enumerate(adj_list):
        for v, book in neighbours.items():
            price = calc_price(1.0, book)
            if price is None or price <= 0:
                continue
            weight = -math.log(price)
            edges.append((u, v, weight))
    return edges


def find_paths_bellman_ford(
    adj_list: AdjacencyList, start_node: NodeID, start_amount: float
) -> List[Path]:
    """Find arbitrage cycles using the Bellman-Ford algorithm."""

    n = len(adj_list)
    edges = _build_edges(adj_list)

    dist = [float("inf")] * n
    pred = [-1] * n
    dist[start_node] = 0.0

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        if not updated:
            break

    result: List[Path] = []
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            cycle_start = v
            for _ in range(n):
                cycle_start = pred[cycle_start]
            cycle = [cycle_start]
            cur = pred[cycle_start]
            while cur not in cycle:
                cycle.append(cur)
                cur = pred[cur]
            cycle.reverse()
            cycle.append(cycle[0])

            amount = start_amount
            path: Path = [(cycle[0], amount)]
            valid = True
            for i in range(len(cycle) - 1):
                book = adj_list[cycle[i]].get(cycle[i + 1])
                if book is None:
                    valid = False
                    break
                amount = calc_price(amount, book)
                if amount is None:
                    valid = False
                    break
                path.append((cycle[i + 1], amount))

            if valid:
                result.append(path)
            break

    return result
