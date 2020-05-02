import os
import yaml
import json
import logging
import asyncio
from cthulhu_src.actions.find_txn import run as find_txn

"""
    Processes the config file and start the search
"""


def run(ctx, config_path):
    log = logging.getLogger('excthulhu')
    log.info(f'Get config from file {config_path}')

    # Get file extension
    file_extension = os.path.splitext(config_path)[-1]

    # Get data from file depending on extension
    if file_extension in ('.yaml', '.yml'):
        with open(config_path, 'r') as yaml_file:
            try:
                data = yaml.safe_load(yaml_file);
            except yaml.YAMLError:
                log.critical('Yaml config parsing error!')
    elif file_extension == '.json':
        with open(config_path) as json_file:
            data = json.load(json_file)
    else:
        log.critical('Config extension must be json or yaml!')

    log.info(
        f'Loaded data: max_depth - {data["max_depth"]}, start - {data["start"]}, '
        f'amount - {data["amount"]}, exchange_list:{", ".join(data["exchange_list"])}')

    # Get proxy list from file if it indicated
    proxy = []
    if 'proxy_list' in data:
        log.info(f'Load proxy from file {data["proxy_list"]}')
        with open(data["proxy_list"], 'r') as f:
            proxy += map(str.rstrip, f.readlines())

    # Get proxy list from config if it indicated
    if 'proxy' in data:
        proxy += data['proxy']

    asyncio.run(find_txn(ctx,
                         data['max_depth'],
                         data['start'],
                         data['amount'],
                         data['exchange_list'],
                         proxy))
