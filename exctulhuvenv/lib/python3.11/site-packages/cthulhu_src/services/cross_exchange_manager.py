"""Utilities for working with cross-exchange currency transfers."""

import os
import math
from os.path import expanduser
from typing import List

from cthulhu_src.services.pair import Order, Pair

AVAILABLE_IO_DIR = expanduser("~/.cache/cthulhu/available_io")


def get_free_transitions(exchanges: List[str]) -> List[Pair]:
    """Return pairs that can be transferred freely between exchanges."""

    if not os.path.isdir(AVAILABLE_IO_DIR):
        # directory with cached available currency lists does not exist
        return []

    input_avalible_currancy_files = [
        os.path.join(AVAILABLE_IO_DIR, f)
        for f in os.listdir(AVAILABLE_IO_DIR)
        if os.path.isfile(os.path.join(AVAILABLE_IO_DIR, f))
        and f.endswith("_input.txt")
    ]

    output_avalible_currancy_files = [
        os.path.join(AVAILABLE_IO_DIR, f)
        for f in os.listdir(AVAILABLE_IO_DIR)
        if os.path.isfile(os.path.join(AVAILABLE_IO_DIR, f))
        and f.endswith("_output.txt")
    ]

    pairs = []
    currency_out = []
    currency_in = []

    for out_file in output_avalible_currancy_files:
        exchange = os.path.split(out_file)[-1].split("_")[0]
        if exchange not in exchanges:
            continue
        with open(out_file) as f:
            content = f.readlines()
            currency_out += [x.strip() for x in content]

    for out_file in input_avalible_currancy_files:
        exchange = os.path.split(out_file)[-1].split("_")[0]
        if exchange not in exchanges:
            continue
        with open(out_file) as f:
            content = f.readlines()
            currency_in += [x.strip() for x in content]

    for cur_out in currency_out:
        for cur_in in currency_in:
            if (
                cur_out.split("_")[1] == cur_in.split("_")[1]
                and cur_out.split("_")[0] != cur_in.split("_")[0]
            ):
                pairs.append(Pair(cur_out, cur_in, [Order(1, math.inf)]))

    return pairs
