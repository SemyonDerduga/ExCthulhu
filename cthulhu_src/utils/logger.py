#!/usr/bin/env python

import logging
import coloredlogs

"""
    Logger object.
"""


def init(debug=False) -> logging.Logger:
    """
    Init logger object

    :param debug: bool is debug
    :return: logger object;
    """

    logger = logging.getLogger('excthulhu')
    level = logging.DEBUG if debug else logging.INFO

    coloredlogs.install(fmt='%(asctime)s - %(levelname)s - %(message)s', logger=logger, level=level)
    return logger
