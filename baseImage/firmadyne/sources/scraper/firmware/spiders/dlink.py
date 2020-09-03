from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse


class DLinkSpider(Spider):
    name = "dlink"
    allowed_domains = ["dlink.com"]
    start_urls = ["http://support.dlink.com/AllPro.aspx"]

    custom_settings = {"CONCURRENT_REQUESTS": 3}

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies={'ServiceTypecookies': "ServiceType=2&ServiceTypeshow=1"}, dont_filter=True)

    def parse(self, response):
        for entry in response.xpath("//tr/td[1]/a/@alt").extract():
            yield Request(
                url=urlparse.urljoin(
                    response.url, "ProductInfo.aspx?m=%s" % entry),
                headers={"Referer": response.url},
                meta={"product": entry},
                callback=self.parse_product)

    def parse_product(self, response):
        for entry in response.xpath("//select[@id='ddlHardWare']/option"):
            rev = entry.xpath(".//text()").extract()[0]
            val = entry.xpath("./@value").extract()[0]

            if val:
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "/ajax/ajax.ashx?action=productfile&ver=%s" % val),
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    meta={"product": response.meta[
                        "product"], "revision": rev},
                    callback=self.parse_json)

    def parse_json(self, response):
        mib = None
        json_response = json.loads(response.body_as_unicode())

        for entry in reversed(json_response["item"]):
            for file in reversed(entry["file"]):
                if file["filetypename"].lower() == "firmware" or file[
                        "isFirmF"] == "1":
                    item = FirmwareLoader(item=FirmwareImage(),
                                          response=response,
                                          date_fmt=["%m/%d/%y"])
                    item.add_value("version",
                                   FirmwareLoader.find_version_period([file["name"]]))
                    item.add_value("date", file["date"])
                    item.add_value("description", file["name"])
                    item.add_value("url", file["url"])
                    item.add_value("build", response.meta["revision"])
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    item.add_value("mib", mib)
                    yield item.load_item()
                elif "MIB" in file["name"]:
                    mib = file["url"]
