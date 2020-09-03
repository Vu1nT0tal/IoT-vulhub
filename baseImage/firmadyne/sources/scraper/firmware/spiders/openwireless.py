from scrapy import Spider

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader


class OpenWirelessSpider(Spider):
    name = "openwireless"
    allowed_domains = ["openwireless.org", "eff.org"]
    start_urls = ["https://www.openwireless.org/router/download"]

    def parse(self, response):
        for href in response.xpath("//a/@href").extract():
            if href.endswith(".img"):
                basename = href.split("/")[-1].split("-")

                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("url", href)
                item.add_value("product", self.name)
                item.add_value("vendor", self.name)
                item.add_value(
                    "version", basename[-1][0: basename[-1].rfind(".img")])
                yield item.load_item()
