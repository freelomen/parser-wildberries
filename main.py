import json
import os
import requests
import time
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


# Сохраняем страницы каталога в файл data_page/index-*.html
def get_data_page(url):
    driver = webdriver.Chrome(service=service, options=options)
    # driver.maximize_window()
    try:
        current_page_number = 1
        driver.get(url=url)
        time.sleep(5)

        scroll_page_down(driver)
        time.sleep(5)

        print(f"Сохраняем страницу: {current_page_number}")
        with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        while is_exist_next_page(driver=driver):
            current_page_number += 1
            driver.get(url=f"{url}?sort=popular&page={current_page_number}")
            time.sleep(5)

            scroll_page_down(driver)
            time.sleep(5)

            print(f"Сохраняем страницу: {current_page_number}")
            with open(f"data_page/index-{current_page_number}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


# Из страниц каталога вытаскиваем ссылки на карточки товаров и сохраняем в item_url_list.json
def get_item_url():
    current_page_number = 1
    item_url_list = []

    for filename in os.listdir("data_page"):
        with open(os.path.join("data_page", filename), 'r', encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        item_cards = soup.find_all("div", class_="product-card j-card-item")

        for item_url in item_cards:
            item_url = f'{item_url.find("a").get("href")}'
            item_url_list.append(item_url)

        current_page_number += 1

    print(f"Ссылки на товары отправлены в json")
    with open('item_url_list.json', 'w') as file:
        json.dump(item_url_list, file, indent=4, ensure_ascii=False)


# Сохраняем карточку товара в файл data_item/item-*.html
def get_item_page(url):
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    try:
        current_item_number = 2
        driver.get(url=url)
        time.sleep(5)

        elements_show = driver.find_elements(By.CLASS_NAME, "collapsible__toggle")
        for item in elements_show:
            item.click()

        scroll_page_down(driver)
        time.sleep(5)

        print(f"Сохраняем карточку товара: {current_item_number}")
        with open(f"data_item/item-{current_item_number}.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_item_info():
    current_item_number = 1
    # items_dict = {}

    for filename in os.listdir("data_item"):
        print(f"\nКарточка: {current_item_number}")
        with open(os.path.join("data_item", filename), 'r', encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        item_title = ' '.join(soup.find("div", class_="product-page__header").find("h1").text.split())
        print(f"Заголовок: {item_title}")

        item_brand = ' '.join(soup.find("div", class_="product-page__header").find("a").text.split())
        print(f"Производитель: {item_brand}")

        item_id = ' '.join(soup.find("span", id="productNmId").text.split())
        print(f"Артикул: {item_id}")

        item_final_price = ' '.join(soup.find("ins", class_="price-block__final-price").text.split())
        print(f"Конечная цена: {item_final_price}")

        if soup.find("del", class_="price-block__old-price"):
            item_old_price = ' '.join(soup.find("del", class_="price-block__old-price").text.split())
            print(f"Старая цена: {item_old_price}")

        item_description = ' '.join(soup.find("p", class_="collapsable__text").text.split())
        print(f"Описание: {item_description}")

        item_params = soup.find_all("div", class_="product-params")[-1].find_all("table", class_="product-params__table")
        for item_param in item_params:
            item_param_caption = ' '.join(item_param.find("caption", class_="product-params__caption").text.split())
            print(f"\n{item_param_caption}")
            item_param = item_param.find("tbody").find_all("tr", class_="product-params__row")
            for item_param_row in item_param:
                item_param_row_th = ' '.join(item_param_row.find("th", class_="product-params__cell").text.split())
                item_param_row_td = ' '.join(item_param_row.find("td", class_="product-params__cell").text.split())
                print(f"{item_param_row_th}: {item_param_row_td}")

        current_item_number += 1

    #     soup = BeautifulSoup(src, 'lxml')
    #     item_cards = soup.find_all("div", class_="product-card j-card-item")
    #
    #     for item_url in item_cards:
    #         item_url = f'{item_url.find("a").get("href")}'
    #         item_url_list.append(item_url)
    #
    #     current_page_number += 1
    #
    # print(f"Ссылки на товары отправлены в json")
    # with open('item_url_list.json', 'w') as file:
    #     json.dump(item_url_list, file, indent=4, ensure_ascii=False)


def main():
    # Сохраняем каталог товаров
    # get_data_page("https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony")
    # get_data_page("https://www.wildberries.ru/catalog/aksessuary/veera")

    # Выдергиваем ссылки карточек товаров
    # get_item_url()

    # Просматриваем карточки товаров
    # get_item_page("https://www.wildberries.ru/catalog/126072691/detail.aspx")
    # get_item_page("https://www.wildberries.ru/catalog/144621264/detail.aspx")

    # Получаем данные товаров
    get_item_info()


if __name__ == '__main__':
    main()
