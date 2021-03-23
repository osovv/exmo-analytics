import hashlib
import hmac
import http
import json
import sys
import time
import urllib


class ExmoApi:
    """Обёртка для работы с EXMO API"""
    def __init__(self, api_key: str, api_secret: str, api_url: str = 'api.exmo.me', api_version: str = 'v1.1'):
        self.api_url = api_url
        self.api_version = api_version
        self.api_key = api_key
        self.api_secret = bytes(api_secret, encoding='utf-8')

    def sha512(self, data):
        h = hmac.new(key=self.api_secret, digestmod=hashlib.sha512)
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    def api_query(self, api_method: str, body: dict = {}):
        """ Выполняет запрос api_method с телом body"""
        body['nonce'] = int(round(time.monotonic() * 1000))
        body = urllib.parse.urlencode(body)

        sign = self.sha512(body)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key": self.api_key,
            "Sign": sign
        }
        conn = http.client.HTTPSConnection(self.api_url)
        conn.request("POST", "/" + self.api_version + "/" + api_method, body, headers)
        response = conn.getresponse().read()

        conn.close()

        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'])
                raise sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()

    def get_courses(self) -> dict[str, str]:
        """ Возвращает курсы всех монет, которые есть на бирже, в долларах"""
        tickers_info = self.api_query('ticker')
        courses = {coin_name: info['last_trade'] for coin_name, info in tickers_info.items()}
        return courses

    def get_all_balances(self) -> dict[str, str]:
        """ Возвращает количество каждой из монет в портфеле"""
        balances = self.api_query('user_info')['balances']
        balances = {coin_name: amount for coin_name, amount in balances.items() if amount != '0'}
        return balances

    def get_all_operations(self):
        """Возвращает все операции аккаунта"""
        operations = self.api_query('wallet_operations')
        return operations
