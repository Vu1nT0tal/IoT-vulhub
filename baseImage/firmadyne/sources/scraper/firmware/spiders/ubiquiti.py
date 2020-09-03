from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse


class UbiquitiSpider(Spider):
    name = "ubiquiti"
    allowed_domains = ["ubnt.com"]
    start_urls = ["http://www.ubnt.com/download/"]

    def parse(self, response):
        for platform in response.xpath(
                "//a[@data-ga-category='download-nav']/@data-slug").extract():
            yield Request(
                url=urlparse.urljoin(response.url, "?group=%s" % (platform)),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_json)

    def parse_json(self, response):
        json_response = json.loads(response.body_as_unicode())

        if "products" in json_response:
            for product in json_response["products"]:
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "?product=%s" % (product["slug"])),
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    meta={"product": product["slug"]},
                    callback=self.parse_json)

        if "url" in response.meta:
            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%Y-%m-%d"])
            item.add_value("url", response.meta["url"])
            item.add_value("product", response.meta["product"])
            item.add_value("date", response.meta["date"])
            item.add_value("description", response.meta["description"])
            item.add_value("build", response.meta["build"])
            item.add_value("version", response.meta["version"])
            item.add_value("sdk", json_response["download_url"])
            item.add_value("vendor", self.name)
            yield item.load_item()

        elif "product" in response.meta:
            for entry in json_response["downloads"]:
                if entry["category__slug"] == "firmware":

                    if entry["sdk__id"]:
                        yield Request(
                            url=urlparse.urljoin(
                                response.url, "?gpl=%s&eula=True" % (entry["sdk__id"])),
                            headers={"Referer": response.url,
                                     "X-Requested-With": "XMLHttpRequest"},
                            meta={"product": response.meta["product"], "date": entry["date_published"], "build": entry[
                                "build"], "url": entry["file_path"], "version": entry["version"], "description": entry["name"]},
                            callback=self.parse_json)
                    else:
                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                        item.add_value("url", entry["file_path"])
                        item.add_value("product", response.meta["product"])
                        item.add_value("date", entry["date_published"])
                        item.add_value("description", entry["name"])
                        item.add_value("build", entry["build"])
                        item.add_value("version", entry["version"])
                        item.add_value("vendor", self.name)
                        yield item.load_item()
