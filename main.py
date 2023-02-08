import json
import os

import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def isExistNextPage(driver):
    try:
        elem = driver.find_element(By.CLASS_NAME, 'pagination'). \
            find_element(By.CLASS_NAME, 'pagination__wrapper'). \
            find_element(By.CLASS_NAME, 'pagination__next')
        return True
    except NoSuchElementException:
        return False


def get_data_page(url):
    print("Подключение установлено")
    options = webdriver.ChromeOptions()
    options.add_argument(
        f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    service = Service('D:\\PythonProjects\\parser-wildberries\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    # driver.maximize_window()

    try:
        current_page_number = 1
        driver.get(url=url)
        time.sleep(5)

        SCROLL_PAUSE_TIME = 2
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        time.sleep(5)
        print(f"Сохраняем страницу: {current_page_number}")
        with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        while (isExistNextPage(driver=driver)):
            current_page_number += 1
            driver.get(url=f"{url}?sort=popular&page={current_page_number}")
            time.sleep(5)

            SCROLL_PAUSE_TIME = 2
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(5)
            print(f"Сохраняем страницу: {current_page_number}")
            with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)

            print(f"Страницы сохранены")
    except Exception as ex:
        print(ex)
    finally:
        print("Подключение закрывается")
        driver.close()

        print("Закрытие драйвера")
        driver.quit()


def get_item_url():
    current_page_number = 1
    current_item_number = 1
    item_url_list = []

    for filename in os.listdir("data_page"):
        print(f"Собираем ссылки: {current_page_number}")
        with open(os.path.join("data_page", filename), 'r', encoding="utf-8") as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        item_cards = soup.find_all("div", class_="product-card j-card-item")
        for item_url in item_cards:
            item_url = f'{item_url.find("a").get("href")}'
            item_url_list.append(item_url)
            # print(f"Товар: {current_item_number}. Ссылка: {item_url}")
            current_item_number += 1
        current_page_number += 1

    with open('item_url_list.json', 'w') as file:
        json.dump(item_url_list, file, indent=4, ensure_ascii=False)


def main():
    # Сохраняем каталог товаров
    # get_data_page("https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony")
    get_data_page("https://www.wildberries.ru/catalog/aksessuary/veera")

    # Выдергиваем ссылки карточек товаров
    get_item_url()


if __name__ == '__main__':
    main()
