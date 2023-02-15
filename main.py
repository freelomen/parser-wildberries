import asyncio
import json
import os
import time

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument(
    f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--headless")
service = Service('D:\\PythonProjects\\parser-wildberries\\chromedriver.exe')


# Проверяем существует ли кнопка перехода на следующую страницу
def is_exist_next_page(driver):
    try:
        elem = driver.find_element(By.CLASS_NAME, 'pagination'). \
            find_element(By.CLASS_NAME, 'pagination__wrapper'). \
            find_element(By.CLASS_NAME, 'pagination__next')
        return True
    except NoSuchElementException:
        return False


# Пролистываем страницу в самый низ
def scroll_page_down(driver):
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# Сохраняем страницы каталога в файл data_page/index-*.html
def get_data_page(url):
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    try:
        current_page_number = 1
        driver.get(url=url)
        time.sleep(2)

        scroll_page_down(driver)

        with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        print(f"Файл index-{current_page_number}.html записан")

        while is_exist_next_page(driver=driver):
            current_page_number += 1
            driver.find_element(By.CLASS_NAME, 'pagination'). \
                find_element(By.CLASS_NAME, 'pagination__wrapper'). \
                find_element(By.CLASS_NAME, 'pagination__next').click()
            # driver.get(url=f"{url}?sort=popular&page={current_page_number}")
            time.sleep(2)

            scroll_page_down(driver)

            with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
            print(f"Файл index-{current_page_number}.html записан")
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


# Из страниц каталога вытаскиваем ссылки на карточки товаров и сохраняем в item_url_list.json
def get_item_url():
    current_page_number = 1
    current_item_number = 1
    item_url_dict = {}

    for filename in os.listdir("data_page"):
        with open(os.path.join("data_page", filename), 'r', encoding="utf-8") as file:
            src = file.read()
        print(f"Файл {filename} открыт")

        soup = BeautifulSoup(src, 'lxml')
        item_cards = soup.find_all("div", class_="product-card j-card-item")

        for item_url in item_cards:
            item_url = f'{item_url.find("a").get("href")}'
            item_url_dict[f"Товар {current_item_number}"] = item_url
            current_item_number += 1

        current_page_number += 1

    with open('item_url_dict.json', 'w', encoding="utf-8") as file:
        json.dump(item_url_dict, file, indent=4, ensure_ascii=False)
    print("Файл item_url_dict.json записан")


# Сохраняем карточку товара в файл data_item/item-*.html
def get_item_page():
    with open("item_url_dict.json", encoding="UTF-8") as file:
        item_url_dict = json.load(file)
    print(f"Файл item_url_dict.json открыт")

    current_item_number = 1

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        for item_url_title, item_url in item_url_dict.items():
            driver.get(url=item_url)
            time.sleep(2)

            elements_show = driver.find_elements(By.CLASS_NAME, "collapsible__toggle")
            for item in elements_show:
                item.click()

            scroll_page_down(driver)

            with open(f"data_item/item-{current_item_number}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
            print(f"Файл item-{current_item_number}.html записан")

            current_item_number += 1
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


# Сохраняем информацию с карточек в items_dict.json
def get_item_info():
    items_dict = []

    for filename in os.listdir("data_item"):
        with open(os.path.join("data_item", filename), 'r', encoding="utf-8") as file:
            src = file.read()
        print(f"Файл {filename} открыт")

        soup = BeautifulSoup(src, 'lxml')

        item_title = ' '.join(soup.find("div", class_="product-page__header").find("h1").text.split())
        item_brand = ' '.join(soup.find("div", class_="product-page__header").find("a").text.split())
        item_id = ' '.join(soup.find("span", id="productNmId").text.split())
        item_final_price = ' '.join(soup.find("ins", class_="price-block__final-price").text.split())

        item_old_price = 0
        if soup.find("del", class_="price-block__old-price"):
            item_old_price = ' '.join(soup.find("del", class_="price-block__old-price").text.split())

        item_description = ' '.join(soup.find("p", class_="collapsable__text").text.split())
        item_params = soup.find_all("div", class_="product-params")[-1].find_all("table",
                                                                                 class_="product-params__table")

        item_title_caption = {}

        for item_param in item_params:
            item_param_caption = ' '.join(item_param.find("caption", class_="product-params__caption").text.split())
            item_param = item_param.find("tbody").find_all("tr", class_="product-params__row")
            item_row = {}

            for item_param_row in item_param:
                item_param_row_th = ' '.join(item_param_row.find("th", class_="product-params__cell").text.split())
                item_param_row_td = ' '.join(item_param_row.find("td", class_="product-params__cell").text.split())
                item_row.update({item_param_row_th: item_param_row_td})

            item_title_caption.update({item_param_caption: item_row})

        items_dict.append(
            {
                "Название": item_title,
                "Производитель": item_brand,
                "Артикул": item_id,
                "Конечная цена": item_final_price,
                "Старая цена": item_old_price,
                "Описание": item_description,
                "О товаре": item_title_caption
            }
        )

    with open("items_dict.json", "w", encoding="utf-8") as file:
        json.dump(items_dict, file, indent=4, ensure_ascii=False)
    print("Файл items_dict.json записан")


def main():
    # Сохраняем каталог товаров
    get_data_page("https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony?page=1&fdlvr=24")

    # Выдергиваем ссылки карточек товаров
    get_item_url()

    # Сохраняем страницы товаров
    get_item_page()

    # Получаем данные товаров
    get_item_info()


if __name__ == '__main__':
    main()
