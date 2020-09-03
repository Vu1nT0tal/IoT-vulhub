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
    base_path = "http://www.tp-link.com/en/"

    def parse(self, response):
        for cid in response.xpath(
                "//select[@id='slcProductCat']//option/@value").extract():
            yield Request(
                url=urlparse.urljoin(
                    self.base_path, "/getMenuList.html?action=getsubcatlist&catid=%s&appPath=us" % cid),
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
                        self.base_path, "/getMenuList.html?action=getsubcatlist&catid=%s&appPath=us" % entry["id"]),
                    meta={"cid": entry["id"]},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_json)
        else:
            yield Request(
                url=urlparse.urljoin(
                    self.base_path, "phppage/down-load-model-list.html?showEndLife=false&catid={}&appPath=us".format(response.meta["cid"])),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_products)

    def parse_products(self, response):
        json_response = json.loads(response.body_as_unicode()) 
        if json_response:
            #description = json_response[0]['title']
            for row in json_response[0]['row']:
                yield Request(
                    url = urlparse.urljoin(self.base_path, row['href']),
                    meta = {"product": row['model'],
                            },
                    callback = self.parse_product_version)

    def parse_product_version(self, response):
        # <div class="hardware-version">
        if response.xpath("//div[@class=\"hardware-version\"]").extract():
            for i in [1, 2]:
                yield Request(
                    url = response.url.replace(".html", "-V{}.html".format(i)),
                    meta = {"product": response.meta['product'],
                            "version": "V{}".format(int(i)+1),
                            },
                    callback = self.parse_product)

        else: #only for v1?
            yield Request(
                url = response.url + "?again=true",
                meta = {"product": response.meta['product'],
                        "version": "V1"
                        },
                callback = self.parse_product)

    def parse_product(self, response):

        #<a href="#Firmware"><span>Firmware</span></a>
        if not response.xpath("//a[@href=\"#Firmware\"]").extract():
            yield None

        description = response.xpath("//div[@class=\"product-name\"]//strong/text()").extract()[0]
        url = response.xpath("//*[@id=\"content_Firmware\"]/table/tbody/tr[1]/th/a/@href").extract()[0]
        date = response.xpath("//*[@id=\"content_Firmware\"]/table/tbody/tr[2]/td[1]/span[2]/text()").extract()[0]

        item = FirmwareLoader(
            item=FirmwareImage(), response=response, date_fmt=["%d/%m/%y"])

        item.add_value("url", url)
        item.add_value("date", item.find_date(date))
        item.add_value("description", description)
        item.add_value("product", response.meta["product"])
        item.add_value("version", response.meta["version"])
        item.add_value("vendor", self.vendor)
        yield item.load_item()
