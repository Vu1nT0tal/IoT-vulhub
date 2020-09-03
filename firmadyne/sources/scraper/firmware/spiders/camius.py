from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urlparse


class CamiusSpider(Spider):
    name = "camius"
    allowed_domains = ["camius.com"]
    start_urls = ["https://camius.com/support/#firmware"]

    def parse(self, response):
        for link in response.xpath('//a'):
            text = link.xpath('text()').extract_first()
            href = link.xpath('@href').extract_first()

            if text is None or href in self.start_urls or "firmware" not in text.lower():
                continue

            yield Request(
                url=urlparse.urljoin(response.url, href),
                headers={"Referer": response.url},
                meta={"product": text},
                callback=self.parse_product_firmware)

    def parse_product_firmware(self, response):
        # Get product name
        product = response.meta["product"]
        
        # Get the product last updated date
        create_date = ''
        for li_elem in response.xpath('//li'):
            if li_elem.xpath('@class').re(r'(\[hide_empty:create_date\])'):
                create_date = li_elem.xpath('.//span[@class="badge"]/text()').extract_first()
            elif li_elem.xpath('@class').re(r'(\[hide_empty:update_date\])'):
                update_date = li_elem.xpath('.//span[@class="badge"]/text()').extract_first()
                break
        else:
            update_date = create_date

        # File list table of downloads
        file_table = response.xpath('//table[@class="wpdm-filelist table table-hover"]')
        for dl_button in file_table.xpath('.//a[@class="inddl btn btn-primary btn-sm"]'):
            href = dl_button.xpath("@href")

            item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt="%B %d, %Y")
            item.add_value("product", product)
            item.add_value("vendor", self.name)
            item.add_value("date", update_date)
            item.add_value("url", href.extract_first())

            yield item.load_item()
