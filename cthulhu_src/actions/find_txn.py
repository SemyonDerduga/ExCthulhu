#!/usr/bin/env python

from cthulhu_src.actions.prepare_data import run as prepare_data
"""
    Find winning transaction.
"""

def run(ctx, max_depth):
    """

    :param ctx: click context object
    :param max_depth: int
    :return:
    """
    log = ctx.obj["logger"]
    log.info(f"Start finding transactions with max depth {max_depth}...")
    prepare_data(ctx)