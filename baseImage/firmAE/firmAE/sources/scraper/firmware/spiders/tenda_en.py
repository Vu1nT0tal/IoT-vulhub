from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse


class TendaENSpider(Spider):
    name = "tenda_en"
    vendor = "tenda"
    allowed_domains = ["tenda.cn"]
    start_urls = ["http://www.tenda.cn/en/services/download.html"]

    def parse(self, response):
        for cid in response.xpath(
                "//div[@class='download_main_list']//li[@data-level='1']/@id").extract():
            yield Request(
                url=urlparse.urljoin(
                    response.url, "../ashx/CategoryList.ashx?parentCategoryId=%s" % cid),
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
        for i in range(0, len(response.xpath("//ul[@id='normaltab2']//a"))):
            if "firmware" in "".join(response.xpath(
                    "//ul[@id='normaltab2']/li[%d]/a//text()" % (i + 1)).extract()).lower():
                for entry in response.xpath(
                        "//div[@id='normalcon2']/div[%d]//table/tr[1]" % (i + 1)):
                    version = entry.xpath("./td[2]//text()").extract()
                    date = entry.xpath("./td[4]//text()").extract()
                    href = entry.xpath("./td[5]//a/@href").extract()[0]

                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                    item.add_value(
                        "version", FirmwareLoader.find_version_period(version))
                    item.add_value("url", href)
                    item.add_value("date", item.find_date(date))
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.vendor)
                    yield item.load_item()
