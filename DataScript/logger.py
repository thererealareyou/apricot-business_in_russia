import os
import json
from datetime import datetime


def start(name_file: str, log_data):

    # Проверка на существование файла log
    if not os.path.exists('log.txt'):

        # print('Файла логов не существует')

        # создание первой записи init
        log_data = [
            {'id': 1,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Текущее время
            "status": 'init',  # Статус проверки
            'database': name_file # имя таблицы которую обновили
            }
        ]

        # создание файла log и добавление в неё первой записи init
        with open('log.txt', 'w') as file:
            json.dump(log_data, file, ensure_ascii=False, indent=4)

    else:

        # print('Файл логов существует')

        # читается файл log
        with open('log.txt', 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Просмотра работы файла log
            # print(data)

        # Поиск последнего id
        current_id = 0

        for record in data:
            current_id = record['id']

        # Создание новой записи
        log_data = {
            'id': current_id + 1,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Текущее время
            "status": 'update',  # Статус проверки
            'file': name_file
        }

        # Добавление записи в общий список
        data.append(log_data)

        # Перезапись log файла
        with open('log.txt', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)