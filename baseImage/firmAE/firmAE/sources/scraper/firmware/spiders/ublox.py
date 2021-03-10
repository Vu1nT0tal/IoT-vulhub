from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

class UbloxSpider(Spider):
    name = "ublox"
    allowed_domains = ["u-blox.com"]
    start_urls = [
        "https://www.u-blox.com/en/product-resources?field_product_tech=All&field_product_form=All&edit-submit-product-search=Go"]

    def parse(self, response):
        for href in response.xpath(
                "//div[@class='view-content']//a/@href").extract():
            yield Request(
                url=urlparse.urljoin(response.url, href),
                headers={"Referer": response.url},
                callback=self.parse_product)

    def parse_product(self, response):
        for entry in response.xpath("//div[@class='view-content']//table"):
            if "firmware update" in " ".join(entry.xpath(
                    "./caption//text()").extract()).lower():
                for link in entry.xpath("./tbody/tr/td[1]/a"):
                    if link.xpath(".//text()"):
                        href = link.xpath("./@href").extract()[0]
                        text = link.xpath(".//text()").extract()[0]

                        product = response.xpath(
                            "//div[@id='--2']/div[3]//div[@class='inside']//text()").extract()[2].upper().split()
                        for category in ["RESOURCES", "FOR", "SERIES"]:
                            if category in product:
                                product.remove(category)

                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response)
                        item.add_value("url", href)
                        item.add_value("product", " ".join(product))
                        item.add_value("description", text)
                        item.add_value("vendor", self.name)
                        yield item.load_item()
