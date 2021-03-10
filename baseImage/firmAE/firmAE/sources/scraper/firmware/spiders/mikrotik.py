from scrapy import Spider
from scrapy.http import FormRequest

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class MikrotikSpider(Spider):
    name = "mikrotik"
    allowed_domains = ["mikrotik.com"]
    start_urls = ["http://www.mikrotik.com/download"]

    def parse(self, response):
        for arch in ["1", "2", "3", "4", "5", "6", "swos"]:
            for pub in ["1", "2", "3", "4", "5"]:
                yield FormRequest(
                    url=urlparse.urljoin(response.url, "/client/ajax.php"),
                    formdata={"action": "getRouterosArch",
                              "arch": arch, "pub": pub},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_product)

    def parse_product(self, response):
        for href in response.xpath("//a/@href").extract():
            if href.endswith(".npk") or href.endswith(".lzb"):
                text = response.xpath("//text()").extract()
                basename = href.split("/")[-1]

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%Y-%b-%d"])
                item.add_value("date", item.find_date(text))
                item.add_value("url", href)
                item.add_value("product", basename[0: basename.rfind("-")])
                item.add_value("vendor", self.name)
                item.add_value(
                    "version", FirmwareLoader.find_version_period(text))
                yield item.load_item()
