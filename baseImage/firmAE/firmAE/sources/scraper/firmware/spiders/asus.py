from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urlparse


class AsusSpider(Spider):
    name = "asus"
    region = "en"
    allowed_domains = ["asus.com"]
    start_urls = ["https://www.asus.com/support/"]

    visited = []

    def parse(self, response):
        if "cid" not in response.meta:
            for category in response.xpath("//div[@class='product-category']//a/@l1_id").extract():
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s" % (self.region, category)),
                    meta={"cid": category},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse)

        elif "sid" not in response.meta:
            for series in response.xpath("//table/id/text()").extract():
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s&s=%s" % (self.region, response.meta["cid"], series)),
                    meta={"cid": response.meta["cid"], "sid": series},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse)

        elif "product" not in response.meta:
            for prod in response.xpath("//table"):
                pid = prod.xpath("./l3_id/text()").extract()[0]
                product = prod.xpath("./m_name/text()").extract()[0]
                mid = prod.xpath("./m_id/text()").extract()[0]

                # choose "Others" = 8
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/Download/%s/%s/%s/%s/%d" % (response.meta["cid"], response.meta["sid"], pid, mid, 8)),
                    meta={"product": product},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_product)

    def parse_product(self, response):
        # types: firmware = 20, gpl source = 30, bios = 3
        for entry in response.xpath(
                "//div[@id='div_type_20']/div[@id='download-os-answer-table']"):
            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%Y/%m/%d"])

            version = FirmwareLoader.find_version_period(
                entry.xpath("./p//text()").extract())
            gpl = None

            # grab first download link (e.g. DLM instead of global or p2p)
            href = entry.xpath("./table//tr[3]//a/@href").extract()[0]

            # attempt to find matching source code entry
            if version:
                for source in response.xpath("//div[@id='div_type_30']/div[@id='download-os-answer-table']"):
                    if version in "".join(source.xpath("./p//text()").extract()):
                        gpl = source.xpath("./table//tr[3]//a/@href").extract()[0]

            item.add_value("version", version)
            item.add_value("date", item.find_date(entry.xpath("./table//tr[2]/td[1]//text()").extract()))
            item.add_value("description", " ".join(entry.xpath("./table//tr[1]//td[1]//text()").extract()))
            item.add_value("url", href)
            item.add_value("sdk", gpl)
            item.add_value("product", response.meta["product"])
            item.add_value("vendor", self.name)
            yield item.load_item()
