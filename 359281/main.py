#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import csv
import os
from stem import Signal
from stem.control import Controller
import time

header = ['Бренд_1','Бренд_2','Название_1','Название_2','Год создания',
    'Артикул','Ноты','Верхние ноты','Страна','Средние ноты','Базовые ноты',
    'Пол','Парфюмер','Группы','Тип кожи','Концентрация','Объем','Описание',
    'Изображение','Ссылка',
]


def renew_connection():
    with Controller.from_port(port=9151) as controller:
        controller.authenticate(password=None)
        controller.signal(Signal.NEWNYM)


def get_page(protocol, host, path, nc=False):
    # , content_type="text/html; charset=utf-8"):
    # Content-Type: application/json; charset=utf-8
    # Content-Type: text/html; charset=utf-8
    if os.path.exists('data') == False:
        os.mkdir('data')

    url = protocol + '://' + host + path
    print('Get page: ' + url)
    local_url = 'data/'+path.replace('?', '___').replace('&', '__').replace('/', '_')
    if os.path.exists(local_url):
        with open(local_url, 'r') as htmlfile:
            return BeautifulSoup(htmlfile.read(), 'lxml')

    if nc:
        # print('Renew connection.')
        renew_connection()
        pass

    session = requests.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}

    session = requests.Session()
    session.headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": host,
        # "Content - Type": content_type,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    }
    response = session.get(url)
    with open(local_url, 'w', newline='') as htmlfile:
        htmlfile.write('<!-- '+url+' -->\n'+response.text)

    # time.sleep(5)
    soup = BeautifulSoup(response.text, 'lxml')

    # app-content
    item = soup.find('app-content')
    if item:
        # del file
        pass

    return soup


def parse_page(soup):
    global header
    resunt = []
    product = {}
    # <div :class="{ 'catalog__list--loading' : loading }" class="catalog__list"
    #   data-component="catalog-products" id="products_cont"><ul class="products products--3">
    item = soup.find('div', id='products_cont')
    lis = item.find('ul').find_all('li')
    for li in lis:
        # print(li.get('class'))
        # ['products__item', 'b-catalogItem']
        # ['products__item', 'js-products__item', 'b-catalogItem']
        if not ('js-products__item' in li.get('class')):
            continue
        # <a class="b-catalogItem__descriptionLink s-link s-link--unbordered"
        #   href="/product/attar-collection-musk-kashmir?source_category=6&amp;preferred=112385">
        # <div class="b-catalogItem__brand">
        # <div class="b-catalogItem__name s-link s-link--unbordered js-product-follow" data-product-sku="112386">
        # <small class="products__hint">
        url = li.find('a').get('href')
        brand = li.find('div', class_='b-catalogItem__brand').text.strip()
        name = li.find('div', class_='b-catalogItem__brand').find_next('div').text.strip()
        # print('-------------------')
        # print('url: ', url)
        # print('brand: ', brand)
        # print('name: ', name)

        for h in header:
            product[h] = '-'

        product['Бренд_1'] = brand
        product['Название_1'] = name
        product['Ссылка'] = 'http://randewoo.ru' + url
        # product = parse_item(get_page('https', 'randewoo.ru', url), 'https://randewoo.ru'+url, product)
        parse_item(get_page('https', 'randewoo.ru', url), product)
        # print(product)
        resunt.append(product)
    return resunt


def parse_item(soup, product):
    img = []
    # <div class="p-productCard__inner">
    # soup = soup.find('div', class_='p-productCard__inner')

    # <div class="b-header__mainTitle">Jean Paul Gaultier</div>
    item = soup.find('div', class_='b-header__mainTitle')
    product['Бренд_2'] = item.text.strip()

    # <div class="b-header__subtitle">Scandal By Night</div>
    item = soup.find('div', class_='b-header__subtitle')
    product['Название_2'] = item.text.strip()

    # a class ="b-catalogItem__photoWrap"
    # item = soup.find('a', class_='b-catalogItem__photoWrap')

    # Загружаем картинки
    # <div class="slick-track" style="opacity: 1; width: 134px; transform: translate3d(0px, 0px, 0px);">
    pics = soup.find('div', class_='slider__inner')
    if pics:
        pics = pics.find_all('div')
        for pic in pics:
            tmp = pic.find('img')
            if tmp:
                img.append('https:' + tmp.get('data-zoom-image'))
    else:
        # Если картинка одна
        # <div class="slider__img">
        pic = soup.find('div', class_='slider__img')
        tmp = pic.find('img')
        img.append('https://' + tmp.get('data-zoom-image'))

    # Загружаем характеристики продукта
    # < div class ="product__tabs small-tabs s-productCard__infoTabs" >
    item = soup.find('div', class_='product__tabs small-tabs s-productCard__infoTabs')
    # <dl class="dl">
    dl = item.find('dl', class_='dl')
    items = dl.find_all('div')

    # for h in header:
    #    product[h] = '-'

    for item in items:
        name = item.find('dt').text.strip()
        value = item.find('dd').text.strip()
        if name in product.keys():
            product[name] = value

    # Описание
    # <div class="collapsable" data-is-kit="false" is_perfume="true" text_length="782">
    item = dl.find_next('div', class_='collapsable').text.strip()
    product['Описание'] = item.replace(';', '.')

    product['Изображение'] = img

    with open('out2.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(product.values())

    return product


def parse_randewoo(count = 60):
    # https://randewoo.ru/category/parfyumeriya?paging=60
    # https://randewoo.ru/category/parfyumeriya?page=2&paging=10&show_more=true
    # 0) +save page
    # 1) Proxy
    # 2) Мультипоток
    # 3) -check ajax
    # 4) +Get page count
    # 5) +call parse_page
    # 6) +call parse_item

    products = []
    page_count = 0

    print('----------------- ')
    print('Парсим Страницу: ', f'https://randewoo.ru/category/parfyumeriya?paging={count}')

    soup = get_page('https', 'randewoo.ru', f'/category/parfyumeriya?paging={count}')

    # Get page count
    # <div class="js-catalog-pager">
    # <ol class="pager pager--frameless">
    # <a class="pager__link" data-block="old_pagination" data-page="2384"
    #   href="/category/parfyumeriya?page=2384&amp;paging=10&amp;show_more=true"><span>2384</span></a>
    item = soup.find('ol', class_='pager pager--frameless')
    item = item.find_all('li')
    page_count = item[-2].find('a').get('data-page')
    print('Всего страниц: ', page_count)
    for n in range(int(page_count)):
        print(f'Загружаем страницу {n + 1} из {page_count}')
        # if n < 359:
        #    continue
        if n == 0:
            products = parse_page(soup)
        else:
            products.append(parse_page(get_page('https', 'randewoo.ru',
                f'/category/parfyumeriya?page={n+1}&paging={count}&show_more=true', True)))
            pass
    return products


def main():
    global header
    with open('out2.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(header)

    products = parse_randewoo()

    # Создание заголовка
    # header = []
    # for product in products:
    #    try:
    #        header.extend(product.keys())
    #    except Exception:
    #        print(product)
    # header = list(set(header))

    with open('out.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile , delimiter=';')
        # Пишем заголовок
        writer.writerow(header)

        for product in products:
            tmp = []
            for h in header:
                tmp.append(product[h] if h in product else '-')
            writer.writerow(tmp)
            pass

if __name__ == '__main__':
    main()
