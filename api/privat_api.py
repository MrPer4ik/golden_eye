import requests

from api import _Api


def _find_rate(response_data, from_currency):
    currency_map = {840: "USD", 643: "RUB"}
    print(from_currency)
    currency_alias = currency_map[from_currency]
    for e in response_data:
        if e["ccy"] == currency_alias:
            return float(e["sale"])

    raise ValueError("Invalid Privat response: USD not found")


class Api(_Api):
    def __init__(self):
        super().__init__("PrivatApi")

    def _update_rate(self, xrate):
        rate = self._get_privat_rate(xrate.from_currency)
        return rate

    def _get_privat_rate(self, from_currency):
        response = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        response_json = response.json()
        self.log.debug(f'Privat answer: {response.text}')
        rate = _find_rate(response_json, from_currency)
        return rate
