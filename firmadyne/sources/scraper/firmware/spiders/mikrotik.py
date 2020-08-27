from scrapy import Spider
from scrapy.http import FormRequest

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class MikrotikSpider(Spider):
    name = "mikrotik"
    allowed_domains = ["mikrotik.com"]
    start_urls = ["https://www.mikrotik.com/download"]

    def parse(self, response):

        for href in response.xpath("//a/@href").extract():
            if href.endswith(".npk") or href.endswith(".lzb"):
                if href.startswith("//"):
                    href = "http:" + href
                text = response.xpath("//text()").extract()
                items = href.split('/')
                version = items[-2]
                basename = items[-1]

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%Y-%b-%d"])
                item.add_value("date", item.find_date(text))
                item.add_value("url", href)
                item.add_value("product", basename[0: basename.rfind("-")])
                item.add_value("vendor", self.name)
                item.add_value(
                    "version", version)
                yield item.load_item()