from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import re
import urlparse


class ActiontecSpider(Spider):
    name = "actiontec"
    allowed_domains = ["actiontec.com"]
    start_urls = ["http://www.actiontec.com/support/"]

    def parse(self, response):
        for link in response.xpath("//div[@class='newboxes2']//a"):
            product = link.xpath(".//text()").extract()[0]
            # some product strings are e.g. "(GT701-WRU) - 54 Mbps Wireless
            # Cable/DSL Router"
            actual = re.match(r"\(([\w ,\\/()-]+?)\)", product)
            if actual:
                product = actual.group(1).replace("(", "").replace(")", "")

            yield Request(
                url=urlparse.urljoin(
                    response.url, link.xpath(".//@href").extract()[0]),
                headers={"Referer": response.url},
                meta={"product": product},
                callback=self.parse_product)

    def parse_product(self, response):
        for image in response.xpath(
                "//div[@id='accordion-2']//tr[position() > 1]"):
            text = image.xpath("./td[2]//a[1]/text()").extract()
            if "firmware" in "".join(text).lower():
                item = FirmwareLoader(item=FirmwareImage(), response=response,
                                      selector=image, date_fmt=["%Y-%m-%d"])
                item.add_xpath("date", "td[1]//text()")
                item.add_value("description", text)
                item.add_xpath("url", "td[2]//a[1]/@href")
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                item.add_value(
                    "version", FirmwareLoader.find_version_period(text))
                yield item.load_item()
