from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class PolycomSpider(Spider):
    name = "polycom"
    allowed_domains = ["polycom.com"]
    start_urls = ["http://support.polycom.com/PolycomService/support/us/support/video/index.html", "http://support.polycom.com/PolycomService/support/us/support/voice/index.html", "http://support.polycom.com/PolycomService/support/us/support/network/index.html",
                  "http://support.polycom.com/PolycomService/support/us/support/cloud_hosted_solutions/index.html", "http://support.polycom.com/PolycomService/support/us/support/strategic_partner_solutions/index.html"]

    download = "/PolycomService/support/us"

    @staticmethod
    def fix_url(url):
        if "://" not in url:
            return PolycomSpider.download + url
        return url

    def parse(self, response):
        if response.xpath("//form[@name='UCagreement']"):
            for href in response.xpath(
                    "//div[@id='productAndDoc']").extract()[0].split('"'):
                if "downloads.polycom.com" in href:
                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%B %d, %Y"])
                    item.add_value("version", response.meta["version"])
                    item.add_value("url", href.encode("utf-8"))
                    item.add_value("date", response.meta["date"])
                    item.add_value("description", response.meta["description"])
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()

        elif response.xpath("//div[@id='ContentChannel']"):
            for entry in response.xpath("//div[@id='ContentChannel']//li"):
                if not entry.xpath("./a"):
                    continue

                text = entry.xpath("./a//text()").extract()[0]
                href = entry.xpath("./a/@href").extract()[0].strip()
                date = entry.xpath("./span//text()").extract()

                path = urlparse.urlparse(href).path

                if any(x in text.lower() for x in ["end user license agreement", "eula", "release notes",
                                                   "mac os", "windows", "guide", "(pdf)", "sample"]) or href.endswith(".pdf"):
                    continue

                elif any(path.endswith(x) for x in [".htm", ".html"]) or "(html)" in text.lower():
                    yield Request(
                        url=urlparse.urljoin(
                            response.url, PolycomSpider.fix_url(href)),
                        meta={"product": response.meta["product"] if "product" in response.meta else text,
                              "date": date, "version": FirmwareLoader.find_version_period([text]), "description": text},
                        headers={"Referer": response.url},
                        callback=self.parse)

                elif path:
                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%B %d, %Y"])
                    item.add_value(
                        "version", FirmwareLoader.find_version_period([text]))
                    item.add_value("url", href.encode("utf-8"))
                    item.add_value("date", item.find_date(date))
                    item.add_value("description", text)
                    # item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
