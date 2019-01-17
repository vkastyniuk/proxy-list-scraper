# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Compose

from proxy_scraper.items import ProxyItem


class HidemynaSpider(scrapy.Spider):
    name = 'hidemyna'
    allowed_domains = ['hidemyna.me']
    start_urls = ['https://hidemyna.me/en/proxy-list/']

    def parse(self, response):
        for item in response.css('table.proxy__t > tbody > tr'):
            loader = ProxyItemLoader(selector=item)
            loader.add_css('ip_address', 'td:nth-child(1)::text')
            loader.add_css('port', 'td:nth-child(2)::text')
            loader.add_css('country_code', 'td:nth-child(3) span:first-child::attr(class)')
            loader.add_css('country', 'td:nth-child(3) div::text')
            loader.add_css('city', 'td:nth-child(3) span:last-child::text')
            loader.add_css('speed', 'td:nth-child(4) p::text')
            loader.add_css('type', 'td:nth-child(5)::text')
            loader.add_css('anonymity', 'td:nth-child(6)::text')
            loader.add_css('last_check', 'td:nth-child(7)::text')

            yield loader.load_item()

        next_page_url = response.css('.is-active + li > a::attr(href)').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse)


class ProxyItemLoader(ItemLoader):
    default_item_class = ProxyItem
    default_input_processor = MapCompose(lambda x: x.strip())
    default_output_processor = TakeFirst()

    country_code_out = Compose(TakeFirst(), lambda x: x.split('-')[-1])
    city_out = Compose(TakeFirst(), lambda x: x.replace('"', '').strip())
