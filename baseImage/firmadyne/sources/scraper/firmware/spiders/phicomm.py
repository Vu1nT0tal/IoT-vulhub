#coding:utf-8

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urlparse

class PhicommSpider(Spider):
    name = "phicomm"
    vendor = "phicomm"
    allowed_domains = ["phicomm.com"]
    #Routers are K serials
    start_urls = ["http://www.phicomm.com/cn/support.php/Soho/search_support/col/6,/keys/K.html"]
    download_path = "http://www.phicomm.com/"

    def parse(self, response):
        head = False
        for tr in response.xpath("//table//tr"):
            if not head:
                head = True
                continue

            description = tr.xpath("./td[2]/text()").extract()[0]
            product = description.split(u'（')[0]
            version = tr.xpath("./td[4]/text()").extract()[0]
            #2017-03-14
            date = tr.xpath("./td[6]/p/text()").extract()[0]
            downloadid = tr.xpath("./td[7]/a/@downloadid").extract()[0]

            #http://www.phicomm.com/cn/support.php/Mobile/Downhit.html?id=437
            firmware_url = "http://www.phicomm.com/cn/support.php/Mobile/Downhit.html?id={}".format(downloadid)
            yield Request(
                url = firmware_url,
                headers={"Referer": response.url},
                meta={
                    "product":product,
                    "version":version,
                    "date":date,
                    'description':description
                },
                callback = self.parse_product)

    def parse_product(self, response):
        import re
        #/cn/Uploads/files/20161024/K1_V22.4.2.15.bin
        print response.text
        path = re.findall(u"(/cn/Uploads/files/.*?\.bin)", response.text)[0]
        url = "http://www.phicomm.com/{}".format(path)

        item = FirmwareLoader(
            item=FirmwareImage())
        item.add_value("url", url),
        item.add_value("product", response.meta['product']),
        item.add_value("date", response.meta['date']),
        item.add_value("version", response.meta['version']),
        item.add_value("vendor", self.vendor),
        item.add_value("description", response.meta['description']),
            
        yield item.load_item()