from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class TISpider(Spider):
    name = "ti"
    allowed_domains = ["ti.com"]
    start_urls = ["http://education.ti.com/en/us/software/search"]

    def parse(self, response):
        for product in response.xpath(
                "//select[@id='placeholdersitebody_0_ctl02_ctl00_ddlClassification']/option[position() > 1]"):
            yield Request(
                url=urlparse.urljoin(response.url + "/",
                                     product.xpath("./@value").extract()[0]),
                meta={"product": product.xpath("./text()").extract()[0]},
                callback=self.parse_product)

    def parse_product(self, response):
        for link in response.xpath(
                "//table[@class='sublayout-etdownloadssearchresults-listing']//tr"):
            if link.xpath("./th[1]/a/text()").extract() and "Operating System" in link.xpath(
                    "./th[1]/a/text()").extract()[0]:
                yield Request(
                    url=urlparse.urljoin(response.url, link.xpath(
                        "./th[1]/a/@href").extract()[0]),
                    meta={"product": response.meta["product"]},
                    callback=self.parse_link)

    def parse_link(self, response):
        # some items will require captcha authentication and pass a cookie e.g.
        # DownloadAuthorizationToken =
        # 7CB8169BFC8848B097BB071118F9E067431714963E3A74A45C8883A70654999980D7F1412CB98B87C802403D74B6A2611122BB3CCEE0B2ACDEEAACA8054B8FFBC4AB2C2CC992649F733AFB2446AA3DC66131E62F0697E9267A374A9E965D1286EC3CFEA1142B5244D497974E5992A3F172581BE78559432DA3A64ECC940D3C43A3C91427EEC5FC712A4ADF64D2FC6C31D62BD8E4417964B31AC6E0B8344EADEA6E81DBB33F522979F3C4FE33ECA4240C188C2C88FAEBC3E0C27AEDF79558E9113F2E7BB2CA261666A26CDA82074F0DC777F2BDB28A5A2588F7F4F67E2A4F04C4DDEE6E3A2A78E2106D2F324986705580070A9016C96007E82332EA1F1D2E9688033F514754555CE186695284B05B24DE6C99F22CCF4F43A7CB5D8AD9053929E3EFDAD40FD20497F1D9ED45BAA4C7CF1C2207C751624D755EBF0C4FF98C9B2E41437E41674C836D80C83C902C4B8B8ADDA23D813D9FA5B3331C36B05CE3C1F479220B7A02
        for link in response.xpath("//tbody[@class='etdownloaditems']//tr"):
            item = FirmwareLoader(item=FirmwareImage(), response=response)
            item.add_value("version", link.xpath(
                ".//td[@class='column-version']//text()").extract()[0].strip())
            item.add_value("url", link.xpath(".//th/a/@href").extract()[0])
            item.add_value("description", link.xpath(
                ".//th/a//text()").extract()[0])
            item.add_value("product", response.meta["product"])
            item.add_value("vendor", self.name)
            yield item.load_item()
