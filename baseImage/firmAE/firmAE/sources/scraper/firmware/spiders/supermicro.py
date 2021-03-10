from scrapy import Spider

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class SupermicroSpider(Spider):
    name = "supermicro"
    allowed_domains = ["supermicro.com"]
    start_urls = ["http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=1",
                  "http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=2", "http://supermicro.com/support/bios/archive.cfm"]

    @staticmethod
    def fix_url(url):
        if "url=" in url:
            return url[url.find('=') + 1:]
        return url

    def parse(self, response):
        if response.xpath(
                "//table[@id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderSupportMiddle_Table_REC']"):
            for row in response.xpath(
                    "//table[@id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderSupportMiddle_Table_REC']/tr[position() > 1]"):
                product = row.xpath(".//td[1]//text()").extract()[0]
                rev = row.xpath(".//td[3]//text()").extract()[0]
                href = row.xpath(".//td[4]//a/@href").extract()[0]

                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("version", rev)
                item.add_value("url", SupermicroSpider.fix_url(href))
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()
        else:
            for row in response.xpath(
                    "//table//table//table//table//table//tr[position() > 1]"):
                product = row.xpath(".//td[1]//text()").extract()[0]
                href = row.xpath(".//td[2]//a/@href").extract()[0]
                rev = row.xpath(".//td[4]//text()").extract()[0]

                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("version", rev)
                item.add_value("url", SupermicroSpider.fix_url(href))
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()
