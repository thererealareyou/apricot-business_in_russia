from bs4 import BeautifulSoup
import requests
import re
import json
import csv
from tqdm import tqdm
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time


header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    'referer':'https://www.google.com/'
}


def parse_consultant(new_data = False):
    data = {}

    def add_data(ID, link, category):
        data[ID] = {
            'link': link,
            'category': category
        }

    def add_additional_data(ID, full_name, name, desc, date):
        data[ID] = {
            'link': data[ID]['link'],
            'full_name': full_name,
            'name': name,
            'desc': desc,
            'date': date,
            'category': data[ID]['category']
        }

    def load_existing_data(filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    if not new_data:
        existing_data = load_existing_data('data-consultant.json')
        data.update(existing_data)

    categories = {'t3204/':'Налоги',
                  't3188/':'Финансы. Бюджет',
                  't57/':'Бухучёт. Статистика',
                  't3192/':'Сельское хозяйство',
                  't42/':'Валютное регулирование'}

    annotations = []
    for category in categories.keys():
        for page in range(1, 5):
            r = requests.get('https://www.consultant.ru/law/hotdocs/' + category + '/?page=' + str(page), headers=header)
            soup = BeautifulSoup(r.text, features="html.parser")
            for annotation_link in soup.find_all('a', href=True, string='см. аннотацию'):
                annotation_url = annotation_link['href']
                annotations.append(annotation_url)
                add_data(annotation_url[annotation_url.rfind('/')+1:annotation_url.rfind('.html')],
                         link=annotation_url, category=categories[category])

    for annotation in tqdm(annotations, desc="Скачивание данных... "):
        r = requests.get('https://www.consultant.ru/' + annotation, headers=header)
        soup = BeautifulSoup(r.text, features="html.parser")
        name = soup.find('h1').text
        full_name = soup.find('div', class_='hot-docs-page__title-link').text
        desc = soup.find('div', class_='hot-docs-page__annotation').text
        date = re.sub(r"[^\d.]", "", soup.find('div', class_='hot-docs-page__document-info-date').text)
        add_additional_data(annotation[annotation.rfind('/')+1:annotation.rfind('.html')], name=name, full_name=full_name, desc=desc, date=date)

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    with open('data.txt', 'w', encoding='utf-8') as file:
        for key in data.keys():
            file.write(data[key]['desc'].replace('\n', '').replace('</s>', '')+'\n')


def parse_all_events():
    data = {}
    links = []

    def add_data(ID, link, name, event_type, place, date, categories):
        data[ID] = {
            'link': link,
            'name': name,
            'type': event_type,
            'place': place,
            'date': date,
            'categories': categories
        }

    def load_existing_data(filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    categories = ['theme-is-agriculture/', 'theme-is-building/']
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    ID = 0


    for category in categories:
        url = 'https://all-events.ru/events/calendar/' + category
        driver.get(url)

        for _ in range(5):
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                show_more_button = driver.find_element(By.XPATH, '//*[@id="catalog-wrapper"]/div[11]/div[3]/a')
                show_more_button.click()
                time.sleep(2)
            except Exception as e:
                pass

            soup = BeautifulSoup(driver.page_source, features="html.parser")
            for tag in soup.find_all('div', class_='event_flex_item'):
                event_tag = tag.find('a', class_='event_name_new')
                event_name = event_tag.text.strip()
                event_link = event_tag['href']
                if event_link in links:
                    continue
                ID += 1
                links.append(event_link)

                try:
                    event_date = tag.find('div', class_='event-date').find('div').text.strip()
                except AttributeError:
                    event_date = '-'

                try:
                    location_tag = tag.find('a', class_='event_info_new_text svg_offline')
                except AttributeError:
                    location_tag = '-'

                try:
                    event_place = location_tag.find('span').text.strip()
                except AttributeError:
                    event_place = '-'

                try:
                    conference_links = tag.find_all('a', class_='event_info_new_text mob_name_event')
                    event_type = [link.find('span').text.strip() for link in conference_links][0]
                except AttributeError:
                    event_type = '-'

                try:
                    event_categories = []
                    tag_items = tag.find_all('div', class_='event_width_content_item')  # Исправлено на tag
                    for tag_item in tag_items:
                        tag_links = tag_item.find_all('a')
                        for tag_link in tag_links:
                            event_categories.append(tag_link.text.strip())
                except AttributeError:
                    event_categories = ['-']

                print("Название события:", event_name)
                print("Ссылка на событие:", event_link)
                print("Дата события:", event_date)
                print("Место события:", event_place)
                print("Тип:", event_type)
                print("Категории:", event_categories)

                add_data(ID, event_link, event_name, event_type, event_place, event_date.replace('\xa0\xa0', ' '), event_categories)

    with open('data_events.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=str)


def parse_gosuslugi():
    data = {}

    def add_data(ID, link, name, event_type, place, date, categories):
        data[ID] = {
            'link': link,
            'name': name,
            'type': event_type,
            'place': place,
            'date': date,
            'categories': categories
        }

    def load_existing_data(filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--js-flags=--expose-gc")
    chrome_options.add_argument("--enable-precise-memory-info")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--user-data-dir=C:\\tmp")
    chrome_options.add_argument("safebrowsing-disable-download-protection")
    ID = 0

    url = 'https://www.gosuslugi.ru/subsidies?sort=MAX_SIZE&selectionStatuses=Active'
    driver = uc.Chrome(options=chrome_options)
    driver.get(url)

    for _ in range(5):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            show_more_button = driver.find_element(By.XPATH, '//*[@id="print-page"]/app-subsidy-main-page/div/app-subsidy-catalog/div/section/div[52]/lib-button/div/button')
            show_more_button.click()
            time.sleep(2)
        except Exception as e:
            pass

        soup = BeautifulSoup(driver.page_source, features="html.parser")
        for tag in soup.find_all('div', class_='mt-24 mt-md-32 subsidy shadow-block ng-star-inserted'):
            ID += 1

            minpromtorg = tag.find(class_='tag small-text').text
            publication_status = tag.find(class_='text-plain').text
            subsidy_title = tag.find(class_='s-name').text
            subsidy_description = tag.find(class_='s-description').div.text.strip()
            subsidy_amount = tag.find_all(class_='title-h4')[0].text.strip()
            application_dates = tag.find_all(class_='title-h4')[1].text.strip()
            more_info_link = tag.find('a', class_='link-plain')['href']

            print(f"Организация: {minpromtorg}")
            print(f"Статус: {publication_status}")
            print(f"Название субсидии: {subsidy_title}")
            print(f"Описание: {subsidy_description}")
            print(f"Размер субсидии: {subsidy_amount}")
            print(f"Даты приёма заявок: {application_dates}")
            print(f"Ссылка для получения дополнительной информации: {more_info_link}")


'''if __name__ == '__main__':
    # parse_all_events()
    # parse_consultant(new_data=False)'''
