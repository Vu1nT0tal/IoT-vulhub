from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

# http://home.centurytel.net/ihd/


class CenturyLinkSpider(Spider):
    name = "centurylink"
    allowed_domains = ["centurylink.com"]
    start_urls = ["http://internethelp.centurylink.com/internethelp/downloads-auto-firmware-q.html"]

    def parse(self, response):
        product = None
        for section in response.xpath("//div[@class='product-content']/div[@class='product-box2']/div"):
            text = section.xpath(".//text()").extract()
            if not section.xpath(".//a"):
                product = text[0].strip()
            else:
                for link in section.xpath(".//a/@href").extract():
                    if link.endswith(".html"):
                        yield Request(
                            url=urlparse.urljoin(response.url, link),
                            meta={"product": product,
                                  "version": FirmwareLoader.find_version(text)},
                            headers={"Referer": response.url},
                            callback=self.parse_download)

    def parse_download(self, response):
        for link in response.xpath("//div[@id='auto']//a"):
            href = link.xpath("./@href").extract()[0]
            text = link.xpath(".//text()").extract()[0]

            if ("downloads" in href or "firmware" in href) and \
                not href.endswith(".html"):
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("version", response.meta["version"])
                item.add_value("url", href)
                item.add_value("description", text)
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                yield item.load_item()
