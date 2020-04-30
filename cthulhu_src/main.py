#!/usr/bin/env python3
import sys
import click

"""
    Endpoint to ExCthulhu
"""

from cthulhu_src.utils import logger

# import commands
from cthulhu_src.routes.find_txn import find
from cthulhu_src.routes.config import config
from cthulhu_src.routes.exchanges import exchanges


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


# include cli commands
cli.add_command(find)
cli.add_command(config)
cli.add_command(exchanges)


def main():
    """
        Before command routing initialize global objects.
        :return: int - exit status
    """
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
        log = logger.init(debug=True)
    else:
        log = logger.init()

    sys.exit(cli(obj={}))


if __name__ == '__main__':
    main()
