# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProxyItem(scrapy.Item):
    ip_address = scrapy.Field()
    port_number = scrapy.Field()
    country_code = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    response_time = scrapy.Field()
    proxy_type = scrapy.Field()
    anonymity = scrapy.Field()
    last_check = scrapy.Field()
