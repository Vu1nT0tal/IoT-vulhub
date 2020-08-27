from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import datetime
import json
import urlparse


class HuaweiZHSpider(Spider):
    name = "huawei_zh"
    vendor = "huawei"
    region = "cn"
    allowed_domains = ["huawei.com"]
    start_urls = ["http://consumer.huawei.com/en/support/downloads/index.htm"]

    def parse(self, response):
        yield Request(
            url=urlparse.urljoin(
                response.url, "/support/services/service/product/category?siteCode=%s" % (self.region)),
            headers={"Referer": response.url,
                     "X-Requested-With": "XMLHttpRequest"},
            callback=self.parse_category)

    def parse_category(self, response):
        json_response = json.loads(response.body_as_unicode())

        for category in json_response:
            yield Request(
                url=urlparse.urljoin(
                    response.url, "/support/services/service/product/list?productID=%s&siteCode=%s" % (category["productId"], self.region)),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_product)

    def parse_product(self, response):
        json_response = json.loads(response.body_as_unicode())

        for product in json_response:
            yield Request(
                url=urlparse.urljoin(
                    response.url, "/support/services/service/file/list?productID=%s&siteCode=%s" % (product["productId"], self.region)),
                meta={"product": product["productCode"]},
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_download)

    def parse_download(self, response):
        json_response = json.loads(response.body_as_unicode())

        for file in json_response:
            if file["subFileType"] == "firmware":
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d/%m/%y"])
                item.add_value("version", file["fileVersion"])
                item.add_value("date", datetime.datetime.fromtimestamp(
                    int(file["releaseDate"]) / 1000).strftime(item.context.get("date_fmt")[0]))
                item.add_value("description", file["fileName"])
                item.add_value("url", file["downloadUrl"])
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.vendor)
                yield item.load_item()
