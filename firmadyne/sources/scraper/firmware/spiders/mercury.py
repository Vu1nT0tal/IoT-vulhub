#coding:utf-8

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urlparse

class MercurySpider(Spider):
    name = "mercury"
    vendor = "mercury"
    allowed_domains = ["mercurycom.com.cn"]
    start_urls = ["http://service.mercurycom.com.cn/download-list.html"]
    download_path = "http://service.mercurycom.com.cn"

    def parse(self, response):
        end_page = int(response.xpath("//*[@class='pagebar']//a[last()]//text()").extract()[0])
        cur_page = 0
        while cur_page < end_page:
            cur_page += 1
            url = 'http://service.mercurycom.com.cn/download-tip-software-{}-0-1.html'.format(cur_page)
            yield Request(
                url = url,
                headers={"Referer": response.url},
                callback = self.parse_list)

    def parse_list(self, response):
        href = response.xpath("//tbody//a//@href").extract()[0]
        yield Request(
            url = urlparse.urljoin(self.download_path, href),
            headers={"Referer": response.url},
            callback = self.parse_product
            )

    def parse_product(self, response):

        tmp = []
        for p in response.xpath("//table//tr//td[2]"):
            tmp.append(p)

        title = tmp[0].xpath("./p/text()").extract()[0]
        url = urlparse.urljoin(self.download_path, tmp[3].xpath("./a/@href").extract()[0])

        def parse(title):

            print title
            product = version = date = None

            tmp = title.split(' ')
            product = tmp[0]

            if len(tmp) == 2:
                #MR814v1_070807 升级程序
                if '_' in tmp[0]:
                    tmp2 = tmp[0].split('_')
                    version = tmp2[0]
                    date = tmp2[1][:6]
                #MWR300T V1(081210)标准版
                elif tmp[1][0] in ['v', 'V']:
                    pass
                else:
                    tmp2 = tmp[1].split('_')
                    version = tmp2[0]
                    date = tmp2[1][:6]

            elif len(tmp) == 3:
                tmp2 = tmp[1].split('_')
                version = tmp2[0]
                date = tmp2[1]

            if version:
                if version[0] not in ['v', 'V']:
                    if 'v' in product:
                        t = product.split('v')
                        product = t[0]
                        version = t[1]

            #MR814v1_070807 升级程序                
            if product.count('_'):
                tmp = product.split('_')
                product = tmp[0]
            if product.count('v'):
                product = product.split('v')[0]
            elif product.count('V'):
                product = product.split('v')[0]


            return product, version, date

        product, version, date = parse(title)

        item = FirmwareLoader(
            item=FirmwareImage())
        item.add_value("url", url),
        item.add_value("product", product),
        #item.add_value("date", date),
        #item.add_value("version", version),
        item.add_value("vendor", self.vendor),
        item.add_value("description", title)
            
        yield item.load_item()