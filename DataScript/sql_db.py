import json
import sqlite3 as sq


# Подключение к базе данных (создаст файл, если его нет)
db = sq.connect('database.db')
# Создание курсора
cursor = db.cursor()


def exists_db(name_table: str):

    command = ''

    if name_table == 'Data_to_check/data_consultant':

        command = '''
        CREATE TABLE IF NOT EXISTS {name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_record NUMERIC DEFAULT '',
        link TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        name TEXT DEFAULT '',
        desc TEXT DEFAULT '',
        date TEXT DEFAULT '',
        category TEXT DEFAULT ''
        )
        '''.format(name="data_consultant")

    elif name_table == 'Data_to_check/data_events':

        command = '''
        CREATE TABLE IF NOT EXISTS {name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_record NUMERIC DEFAULT '',
        link TEXT DEFAULT '',
        name TEXT DEFAULT '',
        type TEXT DEFAULT '',
        place TEXT DEFAULT '',
        date TEXT DEFAULT '',
        categories TEXT DEFAULT ''
        )
        '''.format(name="data_events")

    elif name_table == 'Data_to_check/acts':

        command = '''
        CREATE TABLE IF NOT EXISTS {name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_record NUMERIC DEFAULT '',
        full_act TEXT DEFAULT '',
        short_act TEXT DEFAULT ''
        )
        '''.format(name="acts")

    # Если таблицы нет, создаём её
    db.execute(command)

    db.commit()


def add_record(name_table: str, data: dict):

    if name_table == 'Data_to_check/data_consultant':

        db.execute('''
            INSERT INTO {name} (id_record, link, full_name, name, desc, date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)

        '''.format(name="data_consultant"), (
        data['id_record'], data['link'], data['full_name'], data['name'], data['desc'], data['date'], data['category']))

    elif name_table == 'Data_to_check/data_events':

        db.execute('''
            INSERT INTO {name} (id_record, link, name, type, place, date, categories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''.format(name="data_events"), (
        data['id_record'], data['link'], data['name'], data['type'], data['place'], data['date'], json.dumps(data['categories'])))

    elif name_table == 'Data_to_check/acts':

        db.execute('''
                    INSERT INTO {name} (id_record, full_act, short_act)
                    VALUES (?, ?, ?)
                '''.format(name="acts"), (
        data['id_record'], data['full_act'], data['short_act']))

    db.commit()
