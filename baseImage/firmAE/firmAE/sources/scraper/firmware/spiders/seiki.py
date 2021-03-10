from scrapy import Spider

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader


class SeikiSpider(Spider):
    name = "seiki"
    allowed_domains = ["seiki.com"]
    start_urls = ["http://www.seiki.com/support/download"]

    def parse(self, response):
        for entry in response.xpath(
                "//div[@class='main-container']//p|//div[@class='main-container']//ul"):
            text = entry.xpath(".//text()").extract()

            for href in entry.xpath(".//a/@href").extract():
                if "Firmware" in href:
                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response)
                    item.add_value("url", href)
                    item.add_value(
                        "product", FirmwareLoader.find_product(text))
                    item.add_value("vendor", self.name)
                    yield item.load_item()
