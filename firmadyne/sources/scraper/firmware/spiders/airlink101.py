from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class Airlink101Spider(Spider):
    name = "airlink101"
    allowed_domains = ["airlink101.com"]
    start_urls = ["http://www.airlink101.com/support/index.php?cmd=files"]

    def parse(self, response):
        for entry in response.xpath(
                "//div[@class='menu2']//table//table//table[2]//td[1]//td[2]"):
            desc = entry.xpath(".//text()").extract()

            for link in entry.xpath(".//a"):
                href = link.xpath("./@href").extract()[0]
                text = link.xpath(".//text()").extract()[0]

                if "_a=download" not in href:
                    yield Request(
                        url=urlparse.urljoin(response.url, href),
                        headers={"Referer": response.url},
                        meta={"product": text.strip().split(' ')},
                        callback=self.parse)
                elif "firmware" in text.lower() or "f/w" in text.lower():
                    item = FirmwareLoader(item=FirmwareImage(),
                                          response=response,
                                          date_fmt=["%m/%d/%Y", "%m/%d/%y"])
                    item.add_value("version", FirmwareLoader.find_version(desc))
                    item.add_value("date", item.find_date(desc))
                    item.add_value("description", text)
                    item.add_value("url", href)
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
