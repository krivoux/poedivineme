import json
import csv

import requests

BASE_URL = "https://www.poewiki.net/w/api.php?action=cargoquery&format=json"

cargo = {
    'tables':'items,item_stats,mods',
    'join_on':'items._pageName=item_stats._pageName, item_stats.mod_id=mods.id ',
    'fields':'items.name, mods.stat_text_raw, ROUND(AVG(item_stats.min),0)=min_avg, ROUND(AVG(item_stats.max),0)=max_avg',
    'where': 'items.rarity="Unique" AND items.is_corrupted=False',
    'group_by':'mods.stat_text_raw',
    # 'having':'max_avg-min_avg <> 0',
    'order_by':'items.name',
    'limit': '500',
}




def parseitems(BASE_URL,cargo):
    r = requests.get(BASE_URL,params=cargo | {'offset': 100000})
    list_of_items = [r.json()['cargoquery'][i]['title'] for i in range(len(r.json()['cargoquery']))]
    return print(r.json())




def savecsv(items):

    fieldnames=['name','stat text raw','min_avg','max_avg' ]

    with open('items.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # writes the header row
        writer.writerows(items)  # writes all data rows


parseitems(BASE_URL,cargo)







