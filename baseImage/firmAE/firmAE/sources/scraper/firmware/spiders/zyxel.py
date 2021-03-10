from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urlparse

class ZyXELSpider(Spider):
    name = "zyxel"
    allowed_domains = ["zyxel.com"]
    start_urls = ["http://www.zyxel.com/us/en/support/download_landing.shtml"]

    custom_settings = {"CONCURRENT_REQUESTS": 3}

    def parse(self, response):
        script = json.loads(response.xpath(
            "//div[@id='searchDropUlWrap']/script//text()").extract()[0].split('=')[2].strip()[0: -1])
        for entry in script:
            yield Request(
                url=urlparse.urljoin(
                    response.url, "/us/en/support/SearchResultTab.shtml?c=us&l=en&t=dl&md=%s&mt=Firmware&mt=MIBFile" % script[entry][1]),
                headers={"Referer": response.url},
                meta={"product": script[entry][1]},
                callback=self.parse_product)

    def parse_product(self, response):
        mib = None

        if not response.body:
            return

        for entry in reversed(response.xpath("//table/tbody/tr")):
            if entry.xpath("./td[contains(@class, 'versionTd')]/select"):
                for i in range(
                        0, len(entry.xpath("./td[contains(@class, 'versionTd')]/select/option"))):
                    desc = entry.xpath(
                        "./td[contains(@class, 'typeTd')]/span/text()").extract()[i].lower()

                    if "firmware" in desc:
                        date = entry.xpath(
                            "./td[contains(@class, 'dateTd')]/span/text()").extract()[i]
                        ver = entry.xpath(
                            "./td[contains(@class, 'versionTd')]/select/option/text()").extract()[i]
                        href = entry.xpath(
                            "./td[contains(@class, 'downloadTd')]/div/a[1]/@data-filelink").extract()[i]

                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response, date_fmt=["%m-%d-%Y"])
                        item.add_value("version", ver)
                        item.add_value("date", date)
                        item.add_value("url", href)
                        item.add_value("product", response.meta["product"])
                        item.add_value("mib", mib)
                        item.add_value("vendor", self.name)
                        yield item.load_item()

            else:
                desc = entry.xpath(
                    "./td[contains(@class, 'typeTd')]//text()").extract()[1].lower()

                if "firmware" in desc:
                    date = entry.xpath(
                        "./td[contains(@class, 'dateTd')]//text()").extract()
                    ver = entry.xpath(
                        "./td[contains(@class, 'versionTd')]//text()").extract()
                    href = entry.xpath(
                        "./td[contains(@class, 'downloadTd')]//a/@data-filelink").extract()[0]

                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%m-%d-%Y"])
                    item.add_value("version", ver)
                    item.add_value("date", date)
                    item.add_value("url", href)
                    item.add_value("product", response.meta["product"])
                    item.add_value("mib", mib)
                    item.add_value("vendor", self.name)
                    yield item.load_item()

                elif "mib" in desc:
                    mib = entry.xpath(
                        "./td[contains(@class, 'downloadTd')]//a/@href").extract()[0]
