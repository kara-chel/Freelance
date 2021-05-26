# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RzdRuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    num = scrapy.Field()
    title = scrapy.Field()
    summ = scrapy.Field()
    date = scrapy.Field()
    period = scrapy.Field()
    method = scrapy.Field()
    subject = scrapy.Field()
    # ОКВЭД2
    okved2 = scrapy.Field()
    # ОКПД2
    okpd2 = scrapy.Field()
    # Минимально необходимые требования, предъявляемые к закупаемым товарам (работам, услугам)
    treb = scrapy.Field()
    # ОКЕИ
    okei = scrapy.Field()
    # Наименование единицы измерения
    izmer = scrapy.Field()
    # Сведения о количестве (объёме)
    obem = scrapy.Field()
    # ОКАТО
    okato = scrapy.Field()
    # Наименование региона
    region = scrapy.Field()

    pass
