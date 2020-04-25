import itertools
import collections

N_VERTICES = 6
edges = list(itertools.permutations(list(range(1, N_VERTICES + 1)), 2))

adj_list = collections.defaultdict(set)
for edge in edges:
    adj_list[edge[0]].add(edge[1])
    adj_list[edge[1]].add(edge[0])


def all_paths(start_idx, adj_list, max_len=5):
    res = collections.deque()
    seen = set()
    q = collections.deque()
    path = collections.deque()
    q.append(start_idx)
    path.append(start_idx)
    seen.add(start_idx)
    dfs(start_idx, adj_list, path, seen, start_idx, max_len, res)
    res = [list(deque) for deque in res]
    return res


def dfs(start_idx, adj_list: dict, path: collections.deque, seen: set, cur, max_len: int, res: collections.deque):
    if len(path) == max_len - 1:
        cur_adj = adj_list[cur]
        if start_idx in cur_adj:
            path.append(start_idx)
            res.append(path.copy())
            path.pop()
        return

    for node in adj_list[cur]:
        if node not in seen:
            path.append(node)
            seen.add(node)
            dfs(start_idx, adj_list, path, seen, node, max_len, res)
            seen.remove(node)
            path.pop()

print(all_paths(1, adj_list, 5))