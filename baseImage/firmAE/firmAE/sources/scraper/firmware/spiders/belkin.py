from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class BelkinSpider(Spider):
    name = "belkin"
    allowed_domains = ["belkin.com", "belkin.force.com"]
    start_urls = ["http://www.belkin.com/us/support"]

    def parse(self, response):
        if not response.xpath(
                "//form[@id='productSearchForm']//input[@name='category']/@value").extract()[0]:
            for category in response.xpath("//form[@id='productSearchForm']/div[1]//ul[@class='select-options']//a/@data-id").extract():
                yield FormRequest.from_response(response,
                                                formname="productSearchForm",
                                                formdata={
                                                    "category": category},
                                                callback=self.parse)
        elif not response.xpath("//form[@id='productSearchForm']//input[@name='subCategory']/@value").extract()[0]:
            for subcategory in response.xpath("//form[@id='productSearchForm']/div[2]//ul[@class='select-options']//a/@data-id").extract():
                yield FormRequest.from_response(response,
                                                formname="productSearchForm",
                                                formdata={
                                                    "subCategory": subcategory},
                                                callback=self.parse)
        else:
            for product in response.xpath("//form[@id='productSearchForm']/div[3]//ul[@class='select-options']//a/@data-id").extract():
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "/us/support-product?pid=%s" % (product)),
                    headers={"Referer": response.url},
                    callback=self.parse_product)

    def parse_product(self, response):
        for item in response.xpath("//div[@id='main-content']//a"):
            if "firmware" in item.xpath(".//text()").extract()[0].lower():
                yield Request(
                    url=urlparse.urljoin(
                        response.url, item.xpath(".//@href").extract()[0]),
                    headers={"Referer": response.url},
                    meta={"product": response.xpath("//p[@class='product-part-number']/text()").extract()[0].split(' ')[-1]},
                    callback=self.parse_download)

    def parse_download(self, response):
        iframe = response.xpath(
            "//div[@id='main-content']/iframe/@src").extract()

        if iframe:
            yield Request(
                url=iframe[0],
                headers={"Referer": response.url},
                meta={"product": response.meta["product"]},
                callback=self.parse_redirect)

    def parse_redirect(self, response):
        for text in response.body.split('\''):
            if "articles/" in text.lower() and "download/" in text.lower():
                yield Request(
                    url=urlparse.urljoin(response.url, text),
                    headers={"Referer": response.url},
                    meta={"product": response.meta["product"]},
                    callback=self.parse_kb)

    def parse_kb(self, response):
        # initial html tokenization to find regions segmented by e.g. "======"
        # or "------"
        filtered = response.xpath(
            "//div[@class='sfdc_richtext']").extract()[0].split("=-")

        for entry in [x and x.strip() for x in filtered]:
            resp = HtmlResponse(url=response.url, body=entry,
                                encoding=response.encoding)

            for link in resp.xpath("//a"):
                href = link.xpath("@href").extract()[0]
                if "cache-www" in href:
                    text = resp.xpath("//text()").extract()
                    text_next = link.xpath("following::text()").extract()

                    item = FirmwareLoader(item=FirmwareImage(),
                                          response=response,
                                          date_fmt=["%b %d, %Y", "%B %d, %Y",
                                                    "%m/%d/%Y"])

                    version = FirmwareLoader.find_version_period(text_next)
                    if not version:
                        version = FirmwareLoader.find_version_period(text)

                    item.add_value("version", version)
                    item.add_value("date", item.find_date(text))
                    item.add_value("url", href)
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
