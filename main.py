import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def get_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")

    service = Service('D:\\PythonProjects\\parser-wildberries\\chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        driver.get(url=url)
        print("Подключение установлено")

        print("Ожмдание 10 секунд")
        time.sleep(30)

        print("Пролистываем вниз")
        # target = driver.find_element(By.CLASS_NAME, "pagination")
        # actions = ActionChains(driver)
        # actions.move_to_element(target)
        # actions.perform()

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        SCROLL_PAUSE_TIME = 1

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

        print("Ожмдание 10 секунд")
        time.sleep(10)

        print("Сохранение страницы")
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        print("Ожмдание 10 секунд")
        time.sleep(10)
    except Exception as ex:
        print(ex)
    finally:
        print("Подключение закрывается")
        driver.close()

        print("Закрытие драйвера")
        driver.quit()

    print("Открываем страницу для чтения")
    with open("index.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    item_cards = soup.find_all("div", class_="product-card j-card-item")

    for item_url in item_cards:
        item_url = f'{item_url.find("a").get("href")}'
        print(item_url)

def main():
    # get_data("https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony")
    get_data("https://www.wildberries.ru/catalog/aksessuary/veera")


if __name__ == '__main__':
    main()
