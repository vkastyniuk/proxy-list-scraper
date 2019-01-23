# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Compose

from proxy_scraper.items import ProxyItem


class HideMyNameSpider(scrapy.Spider):
    name = 'hidemyname'
    allowed_domains = ['hidemyna.me']
    start_urls = ['https://hidemyna.me/en/proxy-list/']

    def parse(self, response):
        for item in response.css('table.proxy__t > tbody > tr'):
            proxy_types = item.css('td:nth-child(5)::text').extract_first()
            for proxy_type in proxy_types.split(','):
                loader = ProxyItemLoader(selector=item)
                loader.add_css('ip_address', 'td:nth-child(1)::text')
                loader.add_css('port_number', 'td:nth-child(2)::text')
                loader.add_value('proxy_type', proxy_type)
                loader.add_css('country_code', 'td:nth-child(3) span:first-child::attr(class)')
                loader.add_css('country', 'td:nth-child(3) div::text')
                loader.add_css('city', 'td:nth-child(3) span:last-child::text')
                loader.add_css('response_time', 'td:nth-child(4) p::text')
                loader.add_css('anonymity', 'td:nth-child(6)::text')
                loader.add_css('last_check', 'td:nth-child(7)::text')

                yield loader.load_item()

        next_page_url = response.css('.is-active + li > a::attr(href)').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse)


def country_code_processor(value):
    value = value.split('-')[-1].strip()
    if len(value) == 2:
        return value


class TimeDeltaProcessor(object):
    units = (
        ('seconds', ['seconds']),
        ('minutes', ['minutes', 'min.']),
        ('hours', ['hours', 'h.'])
    )

    def __call__(self, value):
        delta = self._get_time_delta(value)
        return datetime.now(tzlocal()) - delta

    def _get_time_delta(self, value):
        parts = value.split(' ')
        if len(parts) == 2:
            return relativedelta(**{
                self._get_time_unit(parts[1]): int(parts[0])
            })
        elif len(parts) == 4:
            return relativedelta(**{
                self._get_time_unit(parts[1]): int(parts[0]),
                self._get_time_unit(parts[3]): int(parts[2])
            })

    def _get_time_unit(self, value):
        for name, values in self.units:
            for v in values:
                if v in value:
                    return name


class ProxyItemLoader(ItemLoader):
    default_item_class = ProxyItem
    default_input_processor = MapCompose(lambda x: x.strip())
    default_output_processor = TakeFirst()

    port_number_out = Compose(TakeFirst(), int)
    country_code_out = Compose(TakeFirst(), country_code_processor)
    city_out = Compose(TakeFirst(), lambda x: x.replace('"', '').strip())
    response_time_out = Compose(TakeFirst(), lambda x: x.replace('ms', '').strip(), int)
    last_check_out = Compose(TakeFirst(), TimeDeltaProcessor())
