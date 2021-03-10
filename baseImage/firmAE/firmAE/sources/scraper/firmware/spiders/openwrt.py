from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class OpenWRTSpider(Spider):
    name = "openwrt"
    allowed_domains = ["downloads.openwrt.org"]
    start_urls = ["http://downloads.openwrt.org/"]

    def parse(self, response):
        for link in response.xpath("//a"):
            text = link.xpath("text()").extract()[0]
            href = link.xpath("@href").extract()[0]

            yield Request(
                url=urlparse.urljoin(response.url, href),
                headers={"Referer": response.url},
                meta={"version": FirmwareLoader.find_version_period(text)},
                callback=self.parse_url)

    def parse_url(self, response):
        for link in response.xpath("//a"):
            text = link.xpath("text()").extract()[0]
            href = link.xpath("@href").extract()[0]

            if ".." in href:
                continue
            elif href.endswith('/'):
                if "package/" not in text:
                    product = "%s-%s" % (response.meta["product"], text[0: -1]) if "product" in response.meta else text[0: -1]

                    yield Request(
                        url=urlparse.urljoin(response.url, href),
                        headers={"Referer": response.url},
                        meta={"version": response.meta[
                            "version"], "product": product},
                        callback=self.parse_url)
            elif any(href.endswith(x) for x in [".bin", ".elf", ".fdt", ".imx", ".chk", ".trx"]):
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                item.add_value("version", response.meta["version"])
                item.add_value("url", href)
                item.add_value("date", item.find_date(
                    link.xpath("following::text()").extract()))
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                yield item.load_item()
