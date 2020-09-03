#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import re
import urlparse


class NetcoreSpider(Spider):
    name = "netcore"
    allowed_domains = ["netcoretec.com"]
    start_urls = ["http://www.netcoretec.com/softwarelist/&downloadcategoryid=7&isMode=false&pageNo=1&pageSize=1000.html"]
    product_url = 'http://www.netcoretec.com/software_detail/downloadsId={}.html'
    firmware_url = "http://www.netcoretec.com/"

    def parse(self, response):
        th = False
        for tr in response.xpath("//table[1]//tr"):
            if not th:
                th = True
                continue

            href = tr.xpath("./td[@class='name']/a/@href").extract()[0]
            title = tr.xpath("./td[@class='name']/a/@title").extract()[0]
            date = tr.xpath("./td[@class='time']/text()").extract()[0]
            downloadid = re.search('downloadsId=(\d+)\.html', href).group(1)
            url = self.product_url.format(downloadid)

            if not title.count(u"升级固件"):
                continue
            product = re.search('[a-zA-Z0-9\+\-]+',title).group(0)

            # filter firmwares count by limit date(year) >= 2015
            if int(date.split('-')[0]) >= 2015:
                yield Request(
                    url=url,
                    headers={"Referer": response.url},
                    meta={"date": date,
                          "description": title,
                          "product": product,
                          },
                    callback=self.parse_product)

    def parse_product(self, response):
        url =self.firmware_url + response.xpath('//a[@id="downLoadHref"]/@href').extract()[0]

        item = FirmwareLoader(item=FirmwareImage(), response=response)
        item.add_xpath("date", response.meta['date'])
        item.add_value("description",  response.meta['description'])
        item.add_value("url",  url)
        item.add_value("product", response.meta["product"])
        item.add_value("vendor", self.name)
        yield item.load_item()
