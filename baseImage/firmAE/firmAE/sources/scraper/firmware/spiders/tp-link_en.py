from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse

class TPLinkENSpider(Spider):
    name = "tp-link_en"
    vendor = "tp-link"
    allowed_domains = ["tp-link.com"]

    start_urls = ["http://www.tp-link.com/en/download-center.html"]

    def parse(self, response):
        for cid in response.xpath(
                "//select[@id='slcProductCat']//option/@value").extract():
            yield Request(
                url=urlparse.urljoin(
                    response.url, "handlers/handler.ashx?action=getsubcatlist&catid=%s" % cid),
                meta={"cid": cid},
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_json)

    def parse_json(self, response):
        json_response = json.loads(response.body_as_unicode())

        if json_response:
            for entry in json_response:
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "handler.ashx?action=getsubcatlist&catid=%s" % entry["id"]),
                    meta={"cid": entry["id"]},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_json)
        else:
            yield Request(
                url=urlparse.urljoin(
                    response.url, "../download-center.html?async=1&showEndLife=true&catid=%s" % response.meta["cid"]),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_products)

    def parse_products(self, response):
        for link in response.xpath("//a"):
            yield Request(
                url=urlparse.urljoin(
                    response.url, link.xpath("./@href").extract()[0]),
                meta={"product": link.xpath("./@data-model").extract()[0]},
                headers={"Referer": response.url},
                callback=self.parse_product)

    def parse_product(self, response):
        if response.xpath(
                "//dl[@id='dlDropDownBox']") and "build" not in response.meta:
            for entry in response.xpath("//dl[@id='dlDropDownBox']//li/a"):
                href = entry.xpath("./@href").extract()[0]
                text = entry.xpath(".//text()").extract()[0]

                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    meta={"product": response.meta["product"], "build": text},
                    headers={"Referer": response.url},
                    callback=self.parse_product)
        else:
            sdk = None

            for href in reversed(response.xpath(
                    "//div[@id='content_gpl_code']//a/@href").extract()):
                sdk = href

            for entry in response.xpath(
                    "//div[@id='content_firmware']//table"):
                href = entry.xpath("./tbody/tr[1]/th[1]//a/@href").extract()[0]
                text = entry.xpath(
                    "./tbody/tr[1]/th[1]//a//text()").extract()[0]
                date = entry.xpath("./tbody/tr[1]/td[1]//text()").extract()

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d/%m/%y"])
                item.add_value("url", href)
                item.add_value("date", item.find_date(date))
                item.add_value("description", text)
                item.add_value("product", response.meta["product"])
                item.add_value("build", response.meta["build"] if "build" in response.meta else None)
                item.add_value("vendor", self.vendor)
                item.add_value("sdk", sdk)
                yield item.load_item()
