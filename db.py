import sqlite3

conn = sqlite3.connect('sqlite3.db')
cursor = conn.cursor()

# cursor.execute('''SELECT name FROM PRAGMA_TABLE_INFO('mods')''') # Названия полей
# cursor.execute('''SELECT * FROM items''')
cursor.execute('''SELECT * FROM mods''')
# cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name''') # чтобы посмотреть таблицы все в БД
# cursor.execute('''select id,name,hash,min,max from items JOIN mods ON items.Itemid = mods.Itemid where min-max <> 0 ''',)



rows = cursor.fetchall()
print(rows)
conn.close()
