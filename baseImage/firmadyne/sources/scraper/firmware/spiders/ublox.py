from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

class UbloxSpider(Spider):
    name = "ublox"
    allowed_domains = ["u-blox.com"]
    start_urls = [
        "https://www.u-blox.com/en/product-resources?field_product_tech=All&field_product_form=All&edit-submit-product-search=Go&f[0]=field_file_category%3A223"]

    def parse(self, response):
        for a in response.xpath("//table//tr//td[2]//a"):
            title = a.xpath('./@title').extract()[0]
            url = a.xpath('./@href').extract()[0]

            item = FirmwareLoader(
                        item=FirmwareImage(), response=response)
            item.add_value("url", url)
            item.add_value("product", self.parse_product(title))
            item.add_value("description", title)
            item.add_value("vendor", self.name)
            yield item.load_item()


    def parse_product(self, title):
        import re
        p = " for ([a-zA-Z0-9\-_]+)$"
        ret = re.findall(p, title)
        if ret:
            product = ret[0]
        else:
            product = title.replace('u-blox', '').strip().split(' ')[0]
        return product