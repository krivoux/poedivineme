import json
from http.client import responses

import requests

BASE_URL = 'https://www.pathofexile.com/api/trade/search/Mirage'

MODS_URL = 'https://www.pathofexile.com/api/trade/data/stats'



headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0'
}


def getmods(name):
    query = {
        "query": {
            "status": {
                "option": "securable"
            },
            "term": name,  # Пишется term, если не знаешь базу предмета (да и не надо)
            # "type": "Iron Flask",
            "stats": [
                {
                    "type": "and",
                    "filters": []
                }
            ]
        },
        "sort": {
            "price": "asc"
        }
    }

    r = requests.post(BASE_URL, json=query, headers=headers)  # Постим наш квери с параметрами поиска

    if r.status_code == 200:
        pass
    else:
        return print(r.status_code)

    id_of_result = r.json()['id']  # Получаем наши параметры для получения результатов поиска
    result_string = ','.join(r.json()['result'][0:10])  # Берем пока только 10 элементов, иначе отрыг 400 статус код

    FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/' + result_string

    res = requests.get(FETCH_URL, headers=headers,
                       params={'query': id_of_result})  # Забираем первые 10 элементов для обработки

    if res.status_code == 200:
        pass
    else:
        return print(res.status_code)

    # mod_raw_text = res.json()['result'][0]['item']['explicitMods']  # Текст модов на читабельном языке

    explicit_mods_pull = res.json()['result'][0]['item']['extended']['mods'][
        'explicit']  # пул модов со специальными хэшами, которые надо будет потом передавать в POST для поиска с определенными модами и ролами

    explicit_mods_hash = [explicit_mods_pull[i]['magnitudes'][0] for i in range(
        len(explicit_mods_pull))]  # Собсна список с хэшами и ролами (мин/макс), ВАЖНО!: Почему-то 'magnitudes' идет списком, смысла в этом нет, пока выберем первый элемент

    # for i, dict in enumerate(explicit_mods_hash): # халявы не будет
    #     dict['mod_raw_text'] = mod_raw_text[i]
    #
    # print(explicit_mods_hash)

    response = requests.get(MODS_URL, headers=headers)
    if response.status_code == 200:
        pass
    else:
        return print(response.status_code)

    id = 'explicit.stat_3642528642'

    all_raw_texts = response.json()['result'][1]['entries']

    # for mod in all_raw_texts:
    #     if mod['id'] == id:
    #         return print(mod['text'])
    #     else:
    #         pass

    for hash_mod in explicit_mods_hash:
        for raw_text in all_raw_texts:
            if raw_text['id'] == hash_mod['hash']:
                hash_mod['raw_text'] = raw_text['text']
            else:pass


    return print(explicit_mods_hash)



getmods(name="bloodplay")



