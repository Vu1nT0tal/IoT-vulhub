from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class QNAPSpider(Spider):
    name = "qnap"
    allowed_domains = ["qnap.com"]
    start_urls = ["http://www.qnap.com/i/useng/product_x_down"]

    def parse(self, response):
        yield Request(
            url=urlparse.urljoin(
                response.url, "/i/useng/product_x_down/ajax/get_module.php"),
            headers={"Referer": response.url},
            callback=self.parse_products)

    def parse_products(self, response):
        for product in response.xpath("//select/option"):
            text = product.xpath(".//text()").extract()
            value = product.xpath("./@value").extract()

            if value:
                yield Request(
                    # firmware = 1, utility = 4, etc
                    url=urlparse.urljoin(
                        response.url, "/i/useng/product_x_down/product_down.php?II=%s&cat_choose=%d" % (value[0], 1)),
                    meta={"product": text[0]},
                    callback=self.parse_product)

    def parse_product(self, response):
        for row in response.xpath(
                "//div[@class='main_data_block']//table/tr[position() > 1]"):
            text = row.xpath("./td[1]//text()").extract()
            edition = row.xpath("./td[2]//text()").extract()
            date = row.xpath("./td[4]//text()").extract()
            hrefs = row.xpath("./td[5]//a/@href").extract()

            if hrefs:
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%Y/%m/%d"])
                item.add_value(
                    "version", FirmwareLoader.find_version_period(edition))
                item.add_value("build", FirmwareLoader.find_build(edition))
                item.add_value("url", hrefs[0])
                item.add_value("date", item.find_date(date))
                item.add_value("description", text[2].strip())
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                yield item.load_item()
