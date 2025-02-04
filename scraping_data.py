from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
import re
import csv


def search_article(browser):
    while True:
        search_query = input('Введите запрос в строке поиска или введите "выход" \n')
        if search_query == 'выход':
            break

        browser.get('https://www.wildberries.by/')
        search_box = browser.find_element(By.ID, 'searchInput')

        search_box.send_keys(search_query + Keys.RETURN)  # имитирует ввод запроса и нажатие на кнопку поиска
        time.sleep(10)

        full_link_search_query = ('https://www.wildberries.by/' +
                                  f'catalog/0/search.aspx?search={search_query}&page=1')
        browser.get(full_link_search_query)
        time.sleep(1)

        try:
            page_title = browser.title
            print(f'Вы зашли на страницу {page_title} \n')
            time.sleep(1)

            parsed_data = []
            page_number = 1

            while True:
                scroll_page(browser)
                product_cards = browser.find_elements(By.CLASS_NAME, 'product-card__wrapper')

                if not product_cards:
                    print('Такого товара не существует')
                    continue

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

            next_page_button = browser.find_elements(By.CLASS_NAME, 'pagination-next')  #????

            if next_page_button and next_page_button[0].is_enabled():
                page_number += 1
                next_page_link = f'https://www.wildberries.by/catalog/0/search.aspx?search={search_query}&page={page_number}'
                browser.get(next_page_link)
                time.sleep(2)  # Ждем загрузку страницы
            else:
                break  # Если кнопка следующей страницы недействительна, выходим из цикла

            print(f'Общее количество найденных карточек {len(parsed_data)}')

        except Exception as e:
            print(f'Произошла ошибка {str(e)}')
            continue


def scroll_page(browser):
    last_height = browser.execute_script("return document.body.scrollHeight")  #????

    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  #????
        time.sleep(5)
        new_height = browser.execute_script('return document.body.scrollHeight')  #????
        if new_height == last_height:
            break
        last_height = new_height


def save_to_csv(search_query, data):
    with open(f'wildberries_{search_query}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)  # создаем объект
        writer.writerow(['Название', ' Цена', ' URL ссылка'])
        writer.writerows(data)
        print('Данные успешно сохранены в формате csv')


def main():
    browser = webdriver.Chrome()
    try:
        search_article(browser)
    finally:
        browser.quit()


if __name__ == '__main__':
    main()