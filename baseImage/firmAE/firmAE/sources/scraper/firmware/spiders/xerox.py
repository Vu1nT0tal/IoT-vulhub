from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

class XeroxSpider(Spider):
    name = "xerox"
    allowed_domains = ["xerox.com"]
    start_urls = [
        "http://www.support.xerox.com/dnd/productList.jsf?Xlang=en_US"]

    def parse(self, response):
        for href in response.xpath(
                "//div[@class='productResults a2z']//a/@href").extract():
            if "downloads" in href:
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    callback=self.parse_download)

    def parse_download(self, response):
        for firmware in response.xpath(
                "//li[@class='categoryBucket categoryBucketId-7']//li[@class='record ']"):
            product = response.xpath(
                "//div[@class='prodNavHeaderBody']//text()").extract()[0].replace(" Support & Drivers", "")
            date = firmware.xpath(
                ".//ul[@class='dateVersion']//strong/text()").extract()
            version = firmware.xpath(
                ".//ul[@class='dateVersion']//strong/text()").extract()
            href = firmware.xpath(
                ".//a/@href").extract()[0].replace("file-download", "file-redirect")
            text = firmware.xpath(".//a//text()").extract()[0]

            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%b %d, %Y"])
            item.add_value("url", href)
            item.add_value("product", product)
            item.add_value("date", item.find_date(date))
            item.add_value("description", text)
            item.add_value("version", item.find_version_period(version))
            item.add_value("vendor", self.name)
            yield item.load_item()
