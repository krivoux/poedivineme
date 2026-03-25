import json
import csv

import requests

BASE_URL = "https://www.poewiki.net/w/api.php?action=cargoquery&format=json"

cargo = {
    'tables':'items', # item_stats,mods', с модами
    # 'join_on':'items._pageName=item_stats._pageName, item_stats.mod_id=mods.id ', с модами
    'fields':'items.name,items.class,COUNT(items.name)=count', # mods.stat_text_raw', ROUND(AVG(item_stats.min),0)=min_avg, ROUND(AVG(item_stats.max),0)=max_avg моды
    'where': 'items.rarity="Unique" AND items.is_corrupted=False AND items.drop_enabled=True AND items.class <> "Item Piece"',
    'group_by':'items.name,items.class',
    # 'having':'count=1', ЭТО ДЛЯ УБИРАНИЯ ПОВТОРОВ
    # 'group_by':'mods.stat_text_raw,items.name', для модов
    # 'having':'max_avg-min_avg <> 0',для модов
    'order_by':'items.name',
    'limit': '500',

}






def parseitems():
    list_of_items = []

    def pagination():
        offset = 0

        while True:
            print(f"Проверяем наличие данных на строках с {offset} по {offset+500} ")
            r = requests.get(BASE_URL, params=cargo | {'offset': offset})
            if len(r.json()['cargoquery']) != 0:
                offset += 500
            else:
                break
        print(f"Итого можно собрать около {offset} строк")
        return offset

    pagination = pagination()

    for page in range(0,pagination,500):
        r = requests.get(BASE_URL, params=cargo | {'offset': page})
        list_of_items.extend([r.json()['cargoquery'][i]['title'] for i in range(len(r.json()['cargoquery']))])
        print(f"Собираем строки с {page} по {page+500} из {pagination} ")

    return list_of_items



def savecsv(items):

    fieldnames=['name','class','count']
    print('Сохраняем!')

    with open('only_unique_items.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # writes the header row
        writer.writerows(items)  # writes all data rows



savecsv(parseitems())






