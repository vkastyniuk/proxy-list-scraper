# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


# TODO: complete scraper
class FreeProxyListsSpider(scrapy.Spider):
    name = 'freeproxylists'
    allowed_domains = ['freeproxylists.net']
    start_urls = ['http://freeproxylists.net/']

    def parse(self, response):
        for item in response.css('table.DataGrid tr:not(.Caption)'):
            ip_address = item.css('td:nth-child(1) a::text').extract_first()

        next_page_url = response.css('.aui-nav-selected + li > a::attr(href)').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse)
