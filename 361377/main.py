#!/usr/bin/env python3

import os
import csv
import requests
from bs4 import BeautifulSoup
from random_user_agent import get_user_agent
from random_proxies import get_proxies_http, get_proxies_https
from stem import Signal
from stem.control import Controller
from time import sleep


class Parser(object):
    def __init__(self, cache=True, proxies=True):
        self.cache = cache
        self.proxies = proxies
        self.top = True
        self.tor_port = 9151
        self.tor_password = None

        self.urls = []
        self.produtc_urls = []

        self.connection_count = 25
        self.load_count = 0

        # https://na-oboi.ru/vse-naklejki.html?page=49
        self.urls.append('https://na-oboi.ru/vse-naklejki.html')
        for i in range(49-1):
            self.urls.append(f'https://na-oboi.ru/vse-naklejki.html?page={i+2}')

        # https://na-oboi.ru/odnorazovye-trafarety.html
        # https://na-oboi.ru/trafarety-dlya-sten.html
        self.urls.append('https://na-oboi.ru/trafarety-dlya-sten.html')
        for i in range(49-1):
            self.urls.append(f'https://na-oboi.ru/trafarety-dlya-sten.html?page={i+2}')

        self.buld_produtc_urls()

    def renew_connection(self):
        """
        Get new IP addres
        :return:
        """
        with Controller.from_port(port=self.tor_port) as controller:
            controller.authenticate(password=self.tor_password)
            controller.signal(Signal.NEWNYM)

    def get_page(self, url='https:/www.ru'):

        local_url = 'data/' + url.replace('://', '____').replace('?', '___').replace('&', '__').replace('/', '_')
        if os.path.exists(local_url) and self.cache:
            with open(local_url, 'r') as htmlfile:
                print('Get cache page: ' + url)
                return BeautifulSoup(htmlfile.read(), 'lxml')

        self.load_count += 1
        if self.load_count % self.connection_count == 0:
            print('Get new IP adress')
            self.renew_connection()
            sleep(6)

        print('Get page: ' + url)
        # url = protocol + '://' + host + path
        host = url.split('/')[2]

        if not os.path.exists('data'):
            os.mkdir('data')

        session = requests.session()

        if self.proxies:
            # session.proxies = {}
            session.proxies['http'] = get_proxies_http()
            session.proxies['https'] = get_proxies_https()
            # session.proxies['all'] = 'socks5h://127.0.0.1:9150'

        session = requests.Session()
        session.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,imag" +
                      "e/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": host,
            "Content - Type": "text/html; charset=utf-8",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": get_user_agent(),
        }

        response = session.get(url)

        if response.status_code != requests.codes.ok:
            print(f'Error url: {url}')
            print(f'status_code: {response.status_code}')
            return None

        with open(local_url, 'w', newline='') as htmlfile:
            htmlfile.write('<!-- ' + url + ' -->\n' + response.text)

        return BeautifulSoup(response.text, 'lxml')

    def buld_produtc_urls(self):
        for url in self.urls:
            soup = self.get_page(url)
            # <div class="Product-int">
            # <div class="ProductName">
            # <a href="https://na-oboi.ru/dekorativnyye-rozovyye-piony.html">Декоративные розовые пионы
            items = soup.find_all('div', class_='Product-int')
            for item in items:
                self.produtc_urls.append(item.find('div', class_='ProductName').find('a').get('href'))

    def parse(self, url, writer):
        # +Title
        # +Meta description
        # +Название товара
        # +Размеры
        # +Цены
        # +Изображение (имя файла изображения *.jpg)
        product = {}

        soup = self.get_page(url)
        if soup:
            product['title'] = soup.find('title').text.replace(';', '.')
            # <meta name="description" content="
            product['description'] = soup.find('meta', attrs={'name': 'description'}).get('content').replace(';', '.')
            # <h1 class="ProductInfoName" itemprop="name">
            product['name'] = soup.find('h1', class_='ProductInfoName').text.replace(';', '.')
            # <div class="ProductInfoPrice" data-price="1370"><strong id="vprice">1370</strong> руб.
            # product['cost'] = soup.find('div', class_='ProductInfoPrice').get('data-price')
            cost = int(soup.find('div', class_='ProductInfoPrice').get('data-price'))
            # <select name="idvis[9]" class="form-control filld"><option value="200:+0">...
            tmp = soup.find('select', class_='form-control filld')
            sizes = []
            costs = []
            if tmp:
                items = tmp.find_all('option')
                i = 0
                for item in items:
                    i += 1
                    value = item.get('value')
                    value = int(value.split('+')[-1].replace(';', '.'))
                    text = item.text.strip().replace(';', '.')
                    if not (i > 1 and value == 0):
                        # if text != 'Свой размер (Напишите в комментарии)' and text != 'Свой размер':
                        sizes.append(text)
                        costs.append(cost + value)
                product['sizes'] = sizes
                product['costs'] = costs
            else:
                product['sizes'] = ['-']
                product['costs'] = [cost]
            # <div id="rst" class="ProductInfoImage_"> <div class="slider-item">
            #   <img itemprop="image" id="img" src="images/product_images/info_images/6312_0.jpg"
            images = []
            items = soup.find('div', id='rst').find_all('img')
            for item in items:
                img = item.get('src')
                if not img:
                    img = item.get('data-lazy')
                images.append('https://na-oboi.ru/'+img)
            product['images'] = images

            product['url'] = url
            # print(product)
            writer.writerow(product.values())
            # return(product.values())

    def process(self):
        i = 0
        with open('out.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Title',
                             'Meta description',
                             'Название товара',
                             'Размеры',
                             'Цены',
                             'Изображение',
                             'Ссылка'])
            for url in self.produtc_urls:
                # if i > 10:
                #    continue
                self.parse(url, writer)
                i += 1


if __name__ == '__main__':
    p = Parser(cache=True, proxies=True)
    p.process()
