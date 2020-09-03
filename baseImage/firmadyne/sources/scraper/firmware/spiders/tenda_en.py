#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse

class TendaENSpider(Spider):
    name = "tenda_en"
    vendor = "tenda"
    allowed_domains = ["tendacn.com"]
    start_urls = ["http://www.tendacn.com/en/service/download-cata-11-1.html"]
    url = "http://www.tendacn.com/en/service/download-cata-11-{}.html"

    def parse(self, response):
        for page in response.xpath("//div[@class='next-page']/a/text()").extract():
            yield Request(
                url=self.url.format(page),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_product)

    def parse_product(self, response):
        for a in response.xpath("//div[@id='mainbox']//dd/a"):
            url = a.xpath("./@href").extract()[0]
            title = a.xpath("./text()").extract()[0]
            description = title

            items = title.split(' ')
            product = items[0]
            version = items[-1]

            #FH456V1.0 Firmware V10.1.1.1_EN
            #E101（V2.0） Firmware V1.10.0.1_EN
            #G3(V2.0） Firmware V2.0.0.1_EN
            #O3 Firmware V1.0.0.3_EN
            #i6 Firmware V1.0.0.9(3857)_EN
            import re
            p = ur'^(?P<product>([a-uw-zA-UW-Z0-9])+)[\(\uff08]?(V\d\.0)?'
            try:
                ret = re.search(p, items[0].decode('utf-8'))

                if ret:
                    product = ret.group('product')
            except:
                product = item[0]

            item = FirmwareLoader(
                item=FirmwareImage(), response=response)
            item.add_value(
                "version", version)
            item.add_value("url", url)
            item.add_value("product", product)
            item.add_value("vendor", self.vendor)
            yield item.load_item()