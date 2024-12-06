import os
import json
import logger
from sql_db import exists_db, add_record
from my_expections import UnsupportedFileTypeError

files_path = ['Data_to_check/data_events', 'Data_to_check/data_consultant', 'Data_to_check/descriptions_consultant', 'Data_to_check/short_descriptions_consultant', 'Data_to_check/acts']


def search_file_extension(file_path: str) -> str:

    txt_files = ('short_descriptions_consultant', 'descriptions_consultant')

    if file_path.endswith(txt_files):

        return file_path + '.txt'

    else:

        return file_path + '.json'


def exists_file(file_path: str) -> list:

    try:
        extension_file_path = search_file_extension(file_path)

        # Проверка на неподдерживаемый тип файла
        if extension_file_path.endswith('.txt'):
            raise UnsupportedFileTypeError("Данный файл не поддерживается на данный момент")

        if not os.path.exists(extension_file_path):

            print('Файл: "{name}" - не существует'.format(name=file_path))

            return [False]

        else:

            print('Файл: "{name}" - существует'.format(name=file_path))

            # открытие json файла и трансформация информации его в словарь
            with open(extension_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return data

    except UnsupportedFileTypeError as error:
        print('Произошла ошибка при обработке файла "{file_path}": {error}'.format(file_path=file_path, error=error))
        return [False]

    except Exception as error:
        # Обработка других возможных исключений
        print('Произошла ошибка при обработке файла "{file_path}": {error}'.format(file_path=file_path, error=error))
        return [False]


def convector_json_in_dict(name_database: str, data: dict):

    # Раскрытие сырой информации и разбиение на части key, value
    for key, value in data.items():
        # print('key:', key,
        #       'value:', value)

        # запись ключей сырой информации
        list_keys = list()

        for keys in value:
            list_keys.append(keys)

        # проверка списка ключей
        # print('Список искомых ключей: ', list_keys)

        # конвектор информации на обработанную запись которую можно записать в бд
        convert_table = dict()

        # запись уникального id записки
        convert_table['id_record'] = key

        for key_record in list_keys:
            convert_table[key_record] = value[key_record]

        # проверка конвертируемой записи
        # print("Запись в словаре: ", convert_table)

        # Проверка существования таблицы в базе данных
        exists_db(name_database)

        # Добавление в таблицу новой записи
        add_record(name_database, convert_table)


def start_processing():

    # Проверка на наличие файлов
    for file_path in files_path:


        data = exists_file(file_path)


        # Перепроверка существует ли файл. Если data != [False] - значит существует
        if data != [False]:

            # Если существует, то добавить запись в базу данных
            # print("Название искомого файла: ", file_path)
            convector_json_in_dict(file_path, data)

        # logger для отслеживания обновлений таблиц
        logger.start(file_path, data)