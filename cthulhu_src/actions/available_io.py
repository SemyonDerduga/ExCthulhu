import os
import json

import ccxt
import sys
import logging
import hmac, hashlib
from pathlib import Path
from os.path import expanduser
import urllib, http.client

API_KEY = 'AC658D535F4112404C1CC449016CBE1E'
API_SECRET = b'7d1baac2ff2c66134b70ad6745aa6106'
AVAILABLE_IO_DIR = expanduser("~/.cache/cthulhu/available_io")


def run(cxt, exchange):
    log = logging.getLogger('excthulhu')
    log.info(f"Start getting available i/o value for {exchange}...")

    available_cur = []
    not_available = []

    if exchange == 'yobit':

        """
            Каждый новый запрос к серверу должен содержать увеличенное число в диапазоне 1-2147483646
            Поэтому храним число в файле поблизости, каждый раз обновляя его
        """
        nonce_file = "./nonce"
        if not os.path.exists(nonce_file):
            with open(nonce_file, "w") as out:
                out.write('1')

        # Будем перехватывать все сообщения об ошибках с биржи
        class YobitException(Exception):
            pass

        def call_api(**kwargs):
            # При каждом обращении к торговому API увеличиваем счетчик nonce на единицу
            with open(nonce_file, 'r+') as inp:
                nonce = int(inp.read())
                inp.seek(0)
                inp.write(str(nonce + 1))
                inp.truncate()

            payload = {'nonce': nonce}

            if kwargs:
                payload.update(kwargs)
            payload = urllib.parse.urlencode(payload)

            H = hmac.new(key=API_SECRET, digestmod=hashlib.sha512)
            H.update(payload.encode('utf-8'))
            sign = H.hexdigest()

            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Key": API_KEY,
                       "Sign": sign}
            conn = http.client.HTTPSConnection("yobit.net", timeout=60)
            conn.request("POST", "/tapi/", payload, headers)
            response = conn.getresponse().read()

            conn.close()

            try:
                obj = json.loads(response.decode('utf-8'))

                if 'error' in obj and obj['error']:
                    raise YobitException(obj['error'])
                return obj
            except json.decoder.JSONDecodeError:
                raise YobitException('Ошибка анализа возвращаемых данных, получена строка', response)

        ccxt_yobit = ccxt.yobit()

        values = []
        for market in ccxt_yobit.fetch_markets():
            values.append(market['symbol'].split('/')[0])
            values.append(market['symbol'].split('/')[1])
        values = set(values)


        log.info(f"Всего валют {len(values)}")



        for value in values:
            print(value)
            try:
                log.info(f'Получаем кошель для пополнения ({value})')
                resp = call_api(method="GetDepositAddress", coinName=value)
                if not resp["return"]["status"] == "maintenance":
                    available_cur.append(value)
            except YobitException as e:
                print(e)
                not_available.append(value)

        available = [f"{exchange}_{currency}" for currency in list(set(available_cur))]
        log.info(f"Всего доступных для ввода валют {len(available)}")
        log.info(f"Всего недоступных для ввода валют {len(not_available)}")
    elif exchange == 'binance':

        ccxt_yobit = ccxt.binance()

        values = []
        for market in ccxt_yobit.fetch_markets():
            values.append(market['symbol'].split('/')[0])
            values.append(market['symbol'].split('/')[1])
        available = [f"{exchange}_{currency}" for currency in list(set(values))]



    log.info(f"Save avalible currency list for exchange {exchange}")
    cache_dir_path = Path(os.path.expanduser(AVAILABLE_IO_DIR))
    cache_dir_path.mkdir(parents=True, exist_ok=True)

    input_file_path = os.path.join(AVAILABLE_IO_DIR, f"{exchange}_input.txt")
    with open(input_file_path, "w") as f:
        f.write("\n".join(available))

    output_file_path = os.path.join(AVAILABLE_IO_DIR, f"{exchange}_output.txt")
    with open(output_file_path, "w") as f:
        f.write("\n".join(available))

