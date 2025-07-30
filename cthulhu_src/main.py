#!/usr/bin/env python3
import sys
import click

"""
    Endpoint to ExCthulhu
"""

from cthulhu_src.utils import logger

# import commands
from cthulhu_src.routes.config import config
from cthulhu_src.routes.find_txn import find
from cthulhu_src.routes.exchanges import exchanges
from cthulhu_src.routes.available_io import available_io


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


# include cli commands
cli.add_command(find)
cli.add_command(config)
cli.add_command(exchanges)
cli.add_command(available_io)


def main():
    """
    Before command routing initialize global objects.
    :return: int - exit status
    """
    debug = False
    if "--debug" in sys.argv:
        sys.argv.remove("--debug")
        logger.init(debug=True)
        debug = True
    else:
        logger.init()

    sys.exit(cli(obj={"debug": debug}))


if __name__ == "__main__":
    main()
