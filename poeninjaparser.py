import requests, json


def get_exchange_rate():
    URL = 'https://poe.ninja/api/data/currencyoverview?league=Mirage&type=Currency'

    r = requests.get(URL)


    exchange_rate = []

    for currency in r.json()['lines']:
        currency_exchange_rate = {
            'currencyTypeName': currency['currencyTypeName'],
            'chaosEquivalent': currency['chaosEquivalent']
        }

        exchange_rate.append(currency_exchange_rate)
    return exchange_rate




