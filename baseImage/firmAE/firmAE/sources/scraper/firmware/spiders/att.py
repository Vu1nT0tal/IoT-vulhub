from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class ATTSpider(Spider):
    name = "att"
    allowed_domains = ["bellsouth.net"]
    start_urls = ["http://cpems.bellsouth.net/firmware"]

    def parse(self, response):
        for href in response.xpath("//a/@href").extract():
            if href == ".." or href == "/":
                continue
            elif href.endswith(".bin") or href.endswith(".upg"):
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("url", href)
                item.add_value("vendor", self.name)
                yield item.load_item()
            elif "/" in href:
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    callback=self.parse)
