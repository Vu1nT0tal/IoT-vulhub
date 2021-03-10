# -*- coding: utf-8 -*

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse


class TendaZHSpider(Spider):
    name = "tenda_zh"
    vendor = "tenda"
    allowed_domains = ["tenda.com.cn"]
    start_urls = ["http://www.tenda.com.cn/services/download.html"]

    def parse(self, response):
        for href in response.xpath(
                "//div[@class='nav-drop']//a/@href").extract():
            cid = href[href.rfind("-") + 1: href.rfind(".html")]
            if cid.isdigit():
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "../ashx/CategoryList.ashx?parentCategoryId=%s" % (cid)),
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_json)

    def parse_json(self, response):
        json_response = json.loads(response.body_as_unicode())
        for entry in json_response:
            if "PC_Level" in entry:
                if entry["PC_Level"] == "1" or entry["PC_Level"] == "2":
                    yield Request(
                        url=urlparse.urljoin(
                            response.url, "CategoryList.ashx?parentCategoryId=%s" % entry["ID"]),
                        headers={"Referer": response.url,
                                 "X-Requested-With": "XMLHttpRequest"},
                        callback=self.parse_json)
                else:
                    yield Request(
                        url=urlparse.urljoin(
                            response.url, "ProductList.ashx?categoryId=%s" % entry["ID"]),
                        headers={"Referer": response.url,
                                 "X-Requested-With": "XMLHttpRequest"},
                        callback=self.parse_json)
            elif "PRO_Name" in entry:
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "../services/downlist-%s.html" % entry["ID"]),
                    meta={"product": entry["PRO_Model"]},
                    headers={"Referer": response.url},
                    callback=self.parse_product)

    def parse_product(self, response):
        for section in response.xpath("//ul[@id='tab_conbox']/li"):
            if u"升级软件" in "".join(section.xpath("./h3//text()").extract()):
                for entry in section.xpath(".//dd/a"):
                    text = entry.xpath(".//text()").extract()
                    href = entry.xpath("./@href").extract()[0]

                    desc = text[0]
                    # reverse text because hw version can come before version
                    # e.g. "FH330升级软件（V1.0） V1.0.0.24_CN"
                    if len(text) == 1:
                        text = text[0].split()
                        text.reverse()

                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response)
                    item.add_value(
                        "version", FirmwareLoader.find_version_period(text))
                    item.add_value("url", href)
                    item.add_value("product", response.meta["product"])
                    item.add_value("description", desc)
                    item.add_value("vendor", self.vendor)
                    yield item.load_item()
