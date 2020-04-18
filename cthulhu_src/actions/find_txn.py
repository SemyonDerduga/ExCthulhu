#!/usr/bin/env python

def run(ctx, max_depth):
    """

    :param ctx: click context object
    :param max_depth: int
    :return:
    """
    log = ctx.obj["logger"]
    log.info(f"Start finding transactions with max depth {max_depth}...")