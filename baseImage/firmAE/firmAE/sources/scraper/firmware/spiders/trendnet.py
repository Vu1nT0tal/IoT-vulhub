from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

class TrendnetSpider(Spider):
    name = "trendnet"
    allowed_domains = ["trendnet.com"]
    start_urls = ["http://www.trendnet.com/support/"]

    def parse(self, response):
        for entry in response.xpath("//select[@id='SUBTYPE_ID']/option"):
            if entry.xpath(".//text()"):
                text = entry.xpath(".//text()").extract()[0]
                href = entry.xpath("./@value").extract()[0]

                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    meta={"product": text},
                    headers={"Referer": response.url},
                    callback=self.parse_product)

    def parse_product(self, response):
        for tab in response.xpath("//ul[@class='etabs']//a"):
            text = tab.xpath(".//text()").extract()[0]
            href = tab.xpath("./@href").extract()[0]

            if "downloads" in text.lower():
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    meta={"product": response.meta["product"]},
                    headers={"Referer": response.url},
                    callback=self.parse_download)

    def parse_download(self, response):
        for entry in response.xpath("//div[@class='downloadtable']"):
            text = entry.xpath(".//text()").extract()

            if "firmware" in " ".join(text).lower():
                text = entry.xpath(
                    ".//li[@class='maindescription' and position() = 1]//text()").extract()
                date = entry.xpath(
                    ".//li[@class='maindescription' and position() = 2]//text()").extract()
                href = entry.xpath(".//li[@class='maindescription']//a/@onclick").extract()[
                    0].split('\'')[1] + "&button=Continue+with+Download&Continue=yes"

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%m/%d/%Y"])
                item.add_value("url", href)
                item.add_value("product", response.meta["product"])
                item.add_value("date", item.find_date(date))
                item.add_value("version", FirmwareLoader.find_version(text))
                item.add_value("vendor", self.name)
                yield item.load_item()
