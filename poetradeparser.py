import json
from time import sleep
import csv

from poeninjaparser import get_exchange_rate
from poewikiparser import getuniqueitem
import sqlite3
import requests
import numpy as np

BASE_URL = 'https://www.pathofexile.com/api/trade/search/Mirage'

MODS_URL = 'https://www.pathofexile.com/api/trade/data/stats'

cookies = {
    'POESESSID':'e48c958c25491790b1a634ef2eb70291'
}

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0',
    'Content-Type':'application/json'
}

bricked_uniques = []

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

    r = requests.post(BASE_URL, json=query, headers=headers, cookies=cookies)  # Постим наш квери с параметрами поиска
    print(f"x-rate-limit-ip-state: {r.headers['x-rate-limit-ip-state']}")


    if r.status_code == 200:
        pass
    else:
        return print(r.status_code)

    id_of_result = r.json()['id']  # Получаем наши параметры для получения результатов поиска
    result_string = ','.join(r.json()['result'][0:10])  # Берем пока только 10 элементов, иначе отрыг 400 статус код

    FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/' + result_string

    res = requests.get(FETCH_URL, headers=headers,
                       params={'query': id_of_result},cookies=cookies)  # Забираем первые 10 элементов для обработки
    print(f"x-rate-limit-ip-state: {res.headers['x-rate-limit-ip-state']}")



    if res.status_code == 200:
        pass
    else:
        return print(res.status_code)

    # пул модов со специальными хэшами, которые надо будет потом передавать в POST для поиска с определенными модами и ролами
    explicit_mods_pull = res.json()['result'][0]['item']['extended']['mods']['explicit']

    # Собираем список модов\хэшей с мин, максами
    explicit_mods_hash = [explicit_mods_pull[i]['magnitudes'] for i in range(len(explicit_mods_pull)) if explicit_mods_pull[i]['magnitudes'] is not None]

    # Обработка магнитуд аля # to # fire damage, если будет три #, то гг
    for mod in explicit_mods_hash:
        if len(mod) > 1:
            mod[0]['min'] = (float(mod[0]['min']) + float(mod[1]['min']))/2
            mod[0]['max'] = (float(mod[0]['max']) + float(mod[1]['max']))/2
            mod.pop()
        else: pass

    response = requests.get(MODS_URL, headers=headers,cookies=cookies)


    if response.status_code == 200:
        pass
    else:
        return print(response.status_code)

    all_raw_texts = response.json()['result'][1]['entries']


    for hash_mod in explicit_mods_hash:
        for raw_text in all_raw_texts:
            if raw_text['id'] == hash_mod[0]['hash']:
                hash_mod[0]['raw_text'] = raw_text['text']
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
        sleep(3.2)

        # TODO: Надо будет сделать retry, если уперся в рейт лимит


        try:
            mods = getmods(item[0])
        except KeyError:
            bricked_uniques.append({'name':item[0]})

        for mod in mods:
            cursor.execute('''
                           INSERT INTO mods (hash, min, max, raw_text, Itemid)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (mod[0]['hash'], mod[0]['min'], mod[0]['max'], mod[0]['raw_text'], item[1]))
        print('Успех!')
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    print('Данные сохранены в SQLite!')

def getprice():
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    try:
        conn.execute("ALTER TABLE mods ADD COLUMN bo_price INTEGER")
        conn.execute("ALTER TABLE mods ADD COLUMN minroll_price INTEGER")
        conn.execute("ALTER TABLE mods ADD COLUMN maxroll_price INTEGER")
        conn.commit()
    except sqlite3.OperationalError:
        # Column likely already exists; ignore the error
        pass

    query = '''select id,name,hash,min,max,raw_text from mods JOIN items ON mods.Itemid = items.Itemid where maxroll_price-bo_price*(2*(max-min)+1)>=50'''
    # query = '''select id,name,hash,min,max,raw_text from mods JOIN items ON mods.Itemid = items.Itemid where max-min <> 0'''

    cursor.execute(query)
    rows = cursor.fetchall()
    # print(rows[0])

    exchange_rate = get_exchange_rate()


    # ну сука хитер
    for row in rows:
        roll_range = row[4]-row[3]
        print(f"Собираем цены для {row[1]}, Мод: {row[-1]}, id: {row[2]} ")
        for status,min_value,max_value,col_name in [(True,0,0,'bo_price'),(False,row[3],row[3]+0.2*roll_range,'minroll_price'),(False,row[4]-0.2*roll_range,row[4],'maxroll_price')]:
            print(f"Собираем {col_name}")

            sleep(4)

            mod_filters = [
                {
                    "id": row[2],
                    "value": {
                        "min": min_value,
                        "max": max_value
                    },
                    "disabled": status
                }
            ]


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
                            "filters": [] # id: "explicit.stat_4080418644", value: {min: 20}, disabled: false ''' ФОРМАТ ЗАПИСИ СПИСКА ФИЛЬТРОВ'''
                        },
                        {
                            "filters": mod_filters,
                            "type":"and"

                        }
                    ],
                    "filters": {
                        "misc_filters": {
                            "filters": {
                                "corrupted": {
                                    "option": "false"
                                }
                            }
                        }
                    }
                },


                "sort": {
                    "price": "asc",
                }
            }

            # Постим наш квери с параметрами поиска
            r = requests.post(BASE_URL, json=query, headers=headers,cookies=cookies)


            if r.status_code == 200:
                print(f"x-rate-limit-ip-state: {r.headers['x-rate-limit-ip-state']}")
            else:
                r.raise_for_status()



            # Получаем наши параметры для получения результатов поиска
            id_of_result = r.json()['id']

            # Берем пока только 10 элементов, иначе отрыг 400 статус код
            result_string = ','.join(r.json()['result'][0:10])
            number_of_listings = len(r.json()['result'][0:10])


            FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/' + result_string

            # Забираем первые 10 элементов для обработки
            res = requests.get(FETCH_URL, headers=headers, params={'query': id_of_result}, cookies=cookies)


            if res.status_code == 200:
                print(f"x-rate-limit-ip-state: {res.headers['x-rate-limit-ip-state']}")

                prices = [res.json()['result'][i]['listing']['price'] for i in range(number_of_listings)]
                # print(prices)

                prices_in_chaoseq = [listing['amount'] * exchange_rate[listing['currency']]['chaosEquivalent'] for
                                     listing in prices]
                # avg_price = sum(prices_in_chaoseq) / len(prices_in_chaoseq)
                # print(avg_price)

                avg_price = np.median(np.array(prices_in_chaoseq))
                print(avg_price)

                # Названия столбцов оказывается нельзя передавать через плейсхолдеры, о как
                cursor.execute(f"UPDATE mods SET {col_name} = ? WHERE id = ?", (avg_price, row[0]))
                print('Успех!')
            else:
                pass

    conn.commit()
    cursor.close()
    return None

def savebricked():

    fieldnames=['name']
    print('Сохраняем!')

    with open('bricked_uniques.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # writes the header row
        writer.writerows(bricked_uniques)  # writes all data rows


#
# savemods()
# savebricked()
getprice()

def savepricecsv():
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT items.Itemid, name, mods.id, raw_text, min, max,bo_price,maxroll_price,minroll_price FROM mods JOIN items ON mods.Itemid = items.Itemid''')
    rows = cursor.fetchall()
    conn.close()
    with open('output.csv', 'w', newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        # Use writerows to write the entire list at once
        writer.writerows(rows)
    return None


savepricecsv()





