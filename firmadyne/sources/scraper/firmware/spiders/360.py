#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse
import json

class A360Spider(Spider):
    name = "360"
    #allowed_domains = ["luyou.360.cn"]
    json_url = "http://s7.qhres.com/static/ef5bacdd3d93fa90/common_info.js"
    start_urls = ["http://luyou.360.cn/download_center.html?from=nav"]

    def parse(self, response):
        yield Request(
            url=self.json_url,
            headers={"Referer": response.url},
            callback=self.parse_product)

    def parse_product(self, response):
        js = response.text
        if js.startswith("var commonInfo"):
            print response.url
            print js

            p_product = u"id:\"(?P<product>.*?)\""
            p_description = u"title:\"(?P<description>.*?)\""
            p_version = u"romVersions:\"(?P<version>.*?)\""
            p_url = u"romUrl:\"(?P<url>.*?)\""
            p_date = u"updateDate:\"(?P<date>.*?)\""

            import re
            products = re.findall(p_version, js)
            descriptions = re.findall(p_description, js)
            versions = re.findall(p_version, js)
            urls = re.findall(p_url, js)
            dates = re.findall(p_date, js)

            for i in xrange(len(products)):
                product = products[i]
                url = urls[i]
                version = versions[i]
                description = descriptions[i]
                date = dates[i]

                item = FirmwareLoader(
                            item=FirmwareImage(), response=response)
                item.add_value("url", url)
                item.add_value("product", product)
                item.add_value("description", description)
                item.add_value("date", date)
                item.add_value("vendor", self.name)
                yield item.load_item()