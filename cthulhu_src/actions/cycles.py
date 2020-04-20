import networkx as nx
import itertools
from pprint import pprint


def rotate(l, n):
    return l[n:] + l[:n]


def run(states, max_depth, filter_coefficient=0):
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

    edges = [state[0] for state in states]


    #itertools.combinations(states, 2)


    pprint(list(itertools.combinations(set(edges), 2)))
