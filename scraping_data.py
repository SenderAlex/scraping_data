from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
import re
import csv

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_article(browser):
    while True:
        search_query = input('Введите запрос в строке поиска или введите "выход" \n')
        if search_query == 'выход':
            break

        browser.get('https://www.wildberries.by/')
        search_box = browser.find_element(By.ID, 'searchInput')

        search_box.send_keys(search_query + Keys.RETURN)  # имитирует ввод запроса и нажатие на кнопку поиска
        time.sleep(1)

        full_link_search_query = 'https://www.wildberries.by/' + f'catalog/0/search.aspx?search={search_query}'
        browser.get(full_link_search_query)
        time.sleep(1)

        try:
            page_title = browser.title
            print(f'Вы зашли на страницу {page_title} \n')
            time.sleep(1)

            product_cards = browser.find_elements(By.CLASS_NAME, 'product-card__wrapper')

            if not product_cards:
                print('Такого товара не существует')
                continue

            parsed_data = []

            for product_card in product_cards:
                product_brand = product_card.find_element(By.CSS_SELECTOR, 'span.product-card__brand').text
                product_name = product_card.find_element(By.CSS_SELECTOR, 'span.product-card__name').text
                full_product_name = product_brand + ' ' + product_name
                product_prices = product_card.find_element(By.CSS_SELECTOR, 'span.price__wrap').text
                prices = re.findall(r'\d[\d\s,]* р\.', product_prices)
                if prices:
                    discount_price = prices[0]
                else:
                    discount_price = 'нет цены'
                product_link = product_card.find_element(By.CLASS_NAME,
                            'product-card__link.j-card-link.j-open-full-product-card').get_attribute('href')
                parsed_data.append([full_product_name, discount_price, product_link])
            save_to_csv(search_query, parsed_data)

            next_button = browser.find_element(By.CLASS_NAME, 'pagination-next')  # Переход к следующей странице
            if 'disabled' in next_button.get_attribute('class'):
                print("Кнопка 'Следующая' отключена, выходим из цикла.")
                break

            WebDriverWait(browser, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'cookies')))
            next_button.click()  # нажимаем на кнопку
            time.sleep(1)

        except Exception as e:
            print(f'Произошла ошибка {str(e)}')
            continue


def save_to_csv(search_query, data):
    with open(f'wildberries_{search_query}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)  # создаем объект
        writer.writerow(['Название', ' Цена', ' URL ссылка'])
        writer.writerows(data)
        print('Данные успешно сохранены в формат csv')


def main():
    browser = webdriver.Chrome()
    try:
        search_article(browser)
    finally:
        browser.quit()


if __name__ == '__main__':
    main()