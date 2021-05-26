import scrapy


class OldTenderSpider(scrapy.Spider):
    name = 'old_tender'
    allowed_domains = ['old-tender.rzd.ru']
    start_urls = [
        'https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2017',
        'https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2018',
        'https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2019',
        'https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2020',
        'https://old-tender.rzd.ru/tender-plan/public/ru?layer_id=6055&STRUCTURE_ID=704&planned_year=2021',
    ]
    CUSTOM_PROXY = 'http://127.0.0.1:8181'

    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url, callback=self.parse)
            request.meta['proxy'] = self.CUSTOM_PROXY
            yield request
        pass

    def parse(self, response):
        result = {}
        print(f'DEBUG: (url) {response.url}')

        # Paginators
        urls = response.xpath('//div[@class="pager"]//a/@href').getall()
        for url in urls:
            # print(f'DEBUG: (page) {url}')
            request = response.follow(url, callback=self.parse)
            request.meta['proxy'] = self.CUSTOM_PROXY
            yield request

        # Tables
        table = response.xpath('//table[@class="Striped"]')
        trs = table.xpath('./tbody/tr')
        for tr in trs:
            tds = tr.xpath('./td')
            lines = tds[0].xpath('./div//tr')
            for line in lines:
                line_items = line.xpath('./td')
                if line_items[0].css('::text').get().strip() == 'ОКВЭД2':
                    result['okved2'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'ОКПД2':
                    result['okpd2'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == \
                        'Минимально необходимые требования, предъявляемые к закупаемым товарам (работам, услугам)':
                    result['treb'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'ОКЕИ':
                    result['okei'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'Наименование единицы измерения':
                    result['izmer'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'Сведения о количестве (объёме)':
                    result['obem'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'ОКАТО':
                    result['okato'] = line_items[1].css('::text').get().strip().replace(',', ';')
                elif line_items[0].css('::text').get().strip() == 'Наименование региона':
                    result['region'] = line_items[1].css('::text').get().strip().replace(',', ';')

            result['num'] = tds[0].css('::text').get().strip(),
            result['title'] = tds[1].css('::text').get().strip().replace(',', ';'),
            result['summ'] = tds[2].css('::text').get().strip().replace(u'\xa0', ' '),
            result['date'] = tds[3].css('::text').get().strip(),
            result['period'] = tds[4].css('::text').get().strip(),
            result['method'] = tds[5].css('::text').get().strip().replace(',', ';'),
            result['subject'] = tds[6].css('::text').get().strip(),

            yield result
