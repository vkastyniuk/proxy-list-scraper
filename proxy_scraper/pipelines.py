# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import json
import logging

import requests

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.timestamp()

        return json.JSONEncoder.default(self, o)


class ProxyPipeline(object):

    def __init__(self, settings) -> None:
        super().__init__()

        host = settings.get('PROXY_SERVICE_HOST', 'localhost')
        port = settings.get('PROXY_SERVICE_PORT', 5000)
        self.url = 'http://%s:%d/api/proxies/batch' % (host, port)
        self.buffer_length = settings.get('PROXY_SERVICE_BUFFER_LENGTH', 50)
        self.items_buffer = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def send_items(self):
        items_json = json.dumps(self.items_buffer, cls=DateTimeEncoder)
        logger.debug('Send %d proxies', len(self.items_buffer))

        response = requests.put(
            self.url,
            data=items_json,
            headers={'Content-type': 'application/json'}
        )
        if not response.ok:
            logger.error('Invalid response code %s', response.status_code)

        self.items_buffer = []

    def process_item(self, item, spider):
        self.items_buffer.append(dict(item))
        if len(self.items_buffer) >= self.buffer_length:
            self.send_items()

        return item

    def close_spider(self, spider):
        if len(self.items_buffer):
            self.send_items()
