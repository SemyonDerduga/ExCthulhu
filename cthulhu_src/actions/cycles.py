import networkx as nx

def rotate(l, n):
    return l[n:] + l[:n]

def run(states, count=4, filter_coefficient=0):
    """
    Find N cycles in the graph,
    then filter them by filter_coefficient and
    return states list and out coefficient

    :param states:
    :param min_depth:
    :param max_depth:
    :param filter_coefficient:
    :return: (list, float) list and out coefficient
    """

    edges = [(state[0], state[1]) for state in states]

    G = nx.DiGraph(edges)

    cycles = []

    for cycle in nx.simple_cycles(G):
        for cycle_sample in range(len(cycle)):
            cycle = rotate(cycle, cycle_sample)
            cycles.append(cycle + [cycle[0]])

    print(cycles)

