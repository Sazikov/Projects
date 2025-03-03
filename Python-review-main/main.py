import requests
import lxml
import sqlite3
from bs4 import BeautifulSoup

import config


def insert_db (links, names, prices):
    connection = sqlite3.connect(config.db_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS source (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    cursor = connection.cursor()
    n = len(names)
    exist_names = cursor.execute('SELECT name FROM source').fetchall()
    e_n = len(exist_names)
    for i in range(n):
        fl = False
        for j in range(e_n):
            if names[i] == exist_names[j][0]:
                fl = True
                break
        if not fl:
            cursor.execute('INSERT INTO source (name, link, price) VALUES (?, ?, ?)', (names[i], links[i], prices[i]))
    connection.commit()
    connection.close()


def parser(url):
    list_url_products = []
    for i in range(1, 12):
        res = requests.get(f"{url}{i}/")
        soup = BeautifulSoup(res.text, "lxml")
        products = soup.find_all("div", class_="catalog-item")
        for product in products:
            name_product = product.find("div", class_="name")
            link = "https://elektronik-shop.ru" + name_product.find("a", itemprop="url").get("href")
            if link not in list_url_products:
                list_url_products.append(link)

    list_names = []
    list_prices = []

    for url_product in list_url_products:
        res = requests.get(f"{url_product}")
        soup = BeautifulSoup(res.text, "lxml")
        product = soup.find("div", class_="buy-block-content")
        name_product = product.find("div", class_="product-name").text
        price = float("".join(product.find("div", class_="price").find("span", class_ = "value").text.split()))
        list_names.append(name_product)
        list_prices.append(price)

    insert_db(list_url_products, list_names, list_prices)

def print_all():
    connection = sqlite3.connect(config.db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT name, price, link FROM source')
    answers = cursor.fetchall()
    connection.close()
    return answers


def the_output_is_less_than_price(query):
    query = float(query)
    connection = sqlite3.connect(config.db_path)
    cursor = connection.cursor()
    cursor.execute('''                                                              
    SELECT name, price, link
    FROM source
    GROUP BY price
    HAVING AVG(price) < ?
    ORDER BY price DESC
    ''', (query,))
    results = cursor.fetchall()
    connection.close()
    return results


def searchfunc(query):
    answ = print_all()
    result = []
    for x in answ:
        if query.lower() in x[0].lower():
            result.append(x)
    return result

if __name__ == '__main__':
    parser(config.url)