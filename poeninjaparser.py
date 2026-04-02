import requests, json


ninja_trade_dict = {
    'Mirror of Kalandra':'mirror',
    'Exalted Orb':'exalted',
    'Divine Orb':'divine',
    'Blessed Orb':'blessed',
    'Chromatic Orb':'chrome',
    "Gemcutter's Prism":'gcp',
    "Jeweller's Orb":'jewellers',
    'Orb of Scouring':'scour',
    'Orb of Regret':'regret',
    'Orb of Fusing':'fusing',
    'Orb of Chance':'chance',
    'Orb of Alteration':'alt',
    'Orb of Alchemy':'alch',
    'Regal Orb':'regal',
    'Vaal Orb':'vaal'

}

def get_exchange_rate():
    URL = 'https://poe.ninja/api/data/currencyoverview?league=Mirage&type=Currency'

    r = requests.get(URL)


    exchange_rate = {
        ninja_trade_dict.get(currency['currencyTypeName']) : {
            'chaosEquivalent': currency['chaosEquivalent'],
            'curNinjaName': currency['currencyTypeName']
        } for currency in r.json()['lines']
    }

    exchange_rate['chaos'] = {
        'chaosEquivalent': 1,
        'curNinjaName': 'Chaos Orb'
    }

    return exchange_rate

