import json
from time import sleep

from poewikiparser import getuniqueitem
import sqlite3
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
                    "filters": [] #id: "explicit.stat_4080418644", value: {min: 20}, disabled: false ''' ФОРМАТ ЗАПИСИ СПИСКА ФИЛЬТРОВ'''
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

    # пул модов со специальными хэшами, которые надо будет потом передавать в POST для поиска с определенными модами и ролами
    explicit_mods_pull = res.json()['result'][0]['item']['extended']['mods']['explicit']

    # Собсна список с хэшами и ролами (мин/макс), ВАЖНО!: Почему-то 'magnitudes' идет списком, смысла в этом нет, пока выберем первый элемент. СМЫСЛ ЕСТЬ, ТАМ ДЛЯ РОЛЬНЫХ МОДОВ ТИПА ФЛАТОВОГО ДАМАЖА
    explicit_mods_hash = [explicit_mods_pull[i]['magnitudes'][0] for i in range(len(explicit_mods_pull)) if explicit_mods_pull[i]['magnitudes'] is not None]


    response = requests.get(MODS_URL, headers=headers)
    if response.status_code == 200:
        pass
    else:
        return print(response.status_code)

    all_raw_texts = response.json()['result'][1]['entries']


    for hash_mod in explicit_mods_hash:
        for raw_text in all_raw_texts:
            if raw_text['id'] == hash_mod['hash']:
                hash_mod['raw_text'] = raw_text['text']
            else:pass


    return explicit_mods_hash


def savemods():
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    list_of_items = getuniqueitem()

    # Создаём таблицу с нужными полями
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT,
            min INTEGER,
            max INTEGER,
            raw_text TEXT,
            Itemid INTEGER,
            FOREIGN KEY(Itemid) REFERENCES items(Itemid) ON DELETE CASCADE
        )
    ''')

    # Очищаем таблицу (опционально, если хотите перезаписывать данные)
    cursor.execute('DELETE FROM mods')
    cursor.execute('''DELETE FROM sqlite_sequence WHERE name='mods';''')

    # Вставляем данные из списка словарей
    for item in list_of_items:
        print(f"Собираем моды для {item[0]}")
        sleep(1)
        mods = getmods(item[0])
        for mod in mods:
            cursor.execute('''
                           INSERT INTO mods (hash, min, max, raw_text, Itemid)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (mod['hash'], mod['min'], mod['max'], mod['raw_text'], item[1]))
        print('Успех!')
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    print('Данные сохранены в SQLite!')

def getprice():
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    cursor.execute('''select id,name,hash,min,max from items JOIN mods ON items.Itemid = mods.Itemid where min-max <> 0 limit 1''',)
    rows = cursor.fetchall()
    # print(rows[0])

    for row in rows:
        for value in range(row[3], row[4]+1):

            mod_filters = [{
                "id":row[2],
                "value":{"min": value},
                "disabled":False
            }]

            # print(mod_filters)

            query = {
                "query": {
                    "status": {
                        "option": "securable"
                    },
                    "term": row[1],  # Пишется term, если не знаешь базу предмета (да и не надо)
                    # "type": "Iron Flask",
                    "stats": [
                        {
                            "type": "and",
                            "filters": mod_filters # id: "explicit.stat_4080418644", value: {min: 20}, disabled: false ''' ФОРМАТ ЗАПИСИ СПИСКА ФИЛЬТРОВ'''
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

            # Получаем наши параметры для получения результатов поиска
            id_of_result = r.json()['id']

            # Берем пока только 10 элементов, иначе отрыг 400 статус код
            result_string = ','.join(r.json()['result'][0:10])

            FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/' + result_string

            # Забираем первые 10 элементов для обработки
            res = requests.get(FETCH_URL, headers=headers, params={'query': id_of_result})

            if res.status_code == 200:
                pass
            else:
                return print(res.status_code)



            prices= [res.json()['result'][i]['listing']['price'] for i in range(10)]
            print(prices)

    cursor.close()
    return None


savemods()




