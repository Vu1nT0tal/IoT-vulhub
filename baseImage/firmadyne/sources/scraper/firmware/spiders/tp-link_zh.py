# -*- coding: utf-8 -*

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse

class TPLinkZHSpider(Spider):
    name = "tp-link_zh"
    vendor = "tp-link"
    allowed_domains = ["tp-link.com.cn"]
    start_urls = [
        "http://service.tp-link.com.cn/list_download_software_1_0.html"]

    def parse(self, response):
        for product in response.xpath(
                "//table[@id='mainlist']//a/@href").extract():
            yield Request(
                url=urlparse.urljoin(response.url, product),
                headers={"Referer": response.url},
                callback=self.parse_product)

        for page in response.xpath("//div[@id='paging']/a/@href").extract():
            yield Request(
                url=urlparse.urljoin(response.url, page),
                headers={"Referer": response.url},
                callback=self.parse)

    def parse_product(self, response):
        text = response.xpath("//div[@class='download']/table[1]//tr[1]/td[2]//text()").extract()[
            0].encode("ascii", errors="ignore")
        date = response.xpath(
            "//div[@class='download']/table[1]//tr[4]/td[2]//text()").extract()
        href = response.xpath(
            "//div[@class='download']/table[1]//tr[5]/td[2]/a/@href").extract()[0]
        desc = response.xpath(
            "//div[@class='download']/table[1]//tr[1]/td[2]//text()").extract()[0].encode("utf-8")

        build = None
        product = None
        if "_" in text:
            build = text.split("_")[1]
            product = text.split("_")[0]
        elif " " in text:
            product = text.split(" ")[0]

        item = FirmwareLoader(item=FirmwareImage(),
                              response=response, date_fmt=["%Y/%m/%d"])
        item.add_value("url", href.encode("utf-8"))
        item.add_value("date", item.find_date(date))
        item.add_value("description", desc)
        item.add_value("build", build)
        item.add_value("product", product)
        item.add_value("vendor", self.vendor)
        yield item.load_item()
