from scrapy import Spider
from scrapy.http import Request, HtmlResponse

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

# see: http://www.dd-wrt.com/phpBB2/viewtopic.php?t=145255&postdays=0&postorder=asc&start=0
# and http://download.modem-help.co.uk/mfcs-L/LinkSys/


class LinksysSpider(Spider):
    name = "linksys"
    allowed_domains = ["linksys.com"]
    start_urls = ["http://www.linksys.com/us/support/sitemap/"]

    def parse(self, response):
        for link in response.xpath("//div[@class='item']//a/@href").extract():
            yield Request(
                url=urlparse.urljoin(response.url, link),
                headers={"Referer": response.url},
                callback=self.parse_support)

    def parse_support(self, response):
        for link in response.xpath("//div[@id='support-downloads']//a"):
            href = link.xpath("@href").extract()[0]
            text = (link.xpath("text()").extract() or [""])[0]

            if "download" in text.lower():
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    meta={"product": response.xpath(
                        "//span[@class='part-number']/text()").extract()[0].replace("SKU", "").strip()},
                    headers={"Referer": response.url},
                    callback=self.parse_kb)

    def parse_kb(self, response):
        mib = None

        # need to perform some nasty segmentation because different firmware versions are not clearly separated
        # reverse order to get MIB before firmware items
        for entry in reversed(response.xpath(
                "//div[@id='support-article-downloads']/div/p")):
            for segment in reversed(entry.extract().split("<br><br>")):
                resp = HtmlResponse(
                    url=response.url, body=segment, encoding=response.encoding)
                for href in resp.xpath("//a/@href").extract():
                    text = resp.xpath("//text()").extract()

                    if "MIBs" in href:
                        mib = href

                    elif "firmware" in href:
                        text = resp.xpath("//text()").extract()

                        item = FirmwareLoader(
                            item=FirmwareImage(), response=resp, date_fmt=["%m/%d/%Y"])
                        item.add_value("date", item.find_date(text))
                        item.add_xpath("url", "//a/@href")
                        item.add_value("mib", mib)
                        item.add_value("product", response.meta["product"])
                        item.add_value("vendor", self.name)
                        item.add_value(
                            "version", FirmwareLoader.find_version_period(text))
                        yield item.load_item()
