#coding:utf-8
#note: 官网bug，升级软件栏目只能打开一页
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse

class TendaZHSpider(Spider):
    name = "tenda_zh"
    vendor = "tenda"
    allowed_domains = ["tenda.com.cn"]
    start_urls = ["http://www.tenda.com.cn/service/download-cata-11.html"]
    base_url = "http://www.tenda.com.cn/{}"

    def parse(self, response):
        for a in response.xpath("//dd/a"):
            url = a.xpath("./@href").extract()[0]
            text = a.xpath("./text()").extract()[0]

            items = text.split(u'升级软件')
            version = items[-1].strip()
            product = items[0].strip().split(u'（')[0].split(' ')[0]

            yield Request(
                url=self.base_url.format(url),
                headers={"Referer": response.url},
                meta={
                    "product":product,
                    "version":version,
                },
                callback=self.parse_product)

    def parse_product(self, response):
        url = response.xpath("//div[@class='thumbnail']//a/@href").extract()[0]
            
        item = FirmwareLoader(
            item=FirmwareImage(), response=response)
        item.add_value(
            "version", response.meta['version'])
        item.add_value("url", url)
        item.add_value("product", response.meta['product'])
        item.add_value("vendor", self.vendor)
        yield item.load_item()