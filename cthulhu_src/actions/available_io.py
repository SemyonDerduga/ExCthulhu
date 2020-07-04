import os
import json

import logging
import hmac, hashlib
import urllib, http.client
import ccxt

API_KEY = 'AC658D535F4112404C1CC449016CBE1E'
API_SECRET = b'7d1baac2ff2c66134b70ad6745aa6106'


def run(cxt, exchange):
    log = logging.getLogger('excthulhu')
    log.info(f"Start getting available i/o value for {exchange}...")

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

        ccxt_yobit = ccxt.dsx()

        values = []
        for market in ccxt_yobit.fetch_markets():
            values.append(market['symbol'].split('/')[0])
            values.append(market['symbol'].split('/')[1])
        values = set(values)

        log.info(f"Всего валют {len(values)}")

        available = []
        not_available = []

        for value in values:
            try:
                #log.info(f'Получаем кошель для пополнения ({value})')
                call_api(method="GetDepositAddress", coinName=value)
                available.append(value)
            except YobitException as e:
                print(e)
                not_available.append(value)

        log.info(f"Всего доступных для ввода валют {len(available)}")
        log.info(f"Всего недоступных для ввода валют {len(not_available)}")
