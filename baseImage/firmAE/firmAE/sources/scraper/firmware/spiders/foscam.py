from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class FoscamSpider(Spider):
    name = "foscam"
    allowed_domains = ["foscam.com"]
    start_urls = [
        "http://www.foscam.com/download-center/firmware-downloads.html"]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies={'loginEmail': "@.com"}, dont_filter=True)

    def parse(self, response):
        for i in range(0, len(response.xpath("//div[@id='main_right']/span[1]/p")), 7):
            prods = response.xpath("//div[@id='main_right']/span[1]//p[%d]/text()" % (i + 2)).extract()[0].split("\r\n")

            for product in [x for x in prods]:
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_xpath("version", "//div[@id='main_right']/span[1]//p[%d]/text()" % (i + 3))
                item.add_xpath("url", "//div[@id='main_right']/span[1]//p[%d]/a/@href" % (i + 7))
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()

        for i in range(0, len(response.xpath("//div[@id='main_right']/span[2]/p")), 5):
            prods = response.xpath("//div[@id='main_right']/span[2]//p[%d]/text()" % (i + 2)).extract()[0].split(",")

            for product in [x for x in prods]:
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_xpath("version", "//div[@id='main_right']/span[2]//p[%d]/text()" % (i + 3))
                item.add_xpath("url", "//div[@id='main_right']/span[2]//p[%d]/a/@href" % (i + 5))
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()
