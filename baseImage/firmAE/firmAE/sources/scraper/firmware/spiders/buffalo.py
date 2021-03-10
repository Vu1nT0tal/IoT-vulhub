from scrapy import Spider
from scrapy.http import FormRequest

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json

class BuffaloSpider(Spider):
    name = "buffalo"
    allowed_domains = ["buffalotech.com", "cdn.cloudfiles.mosso.com"]
    start_urls = ["http://www.buffalotech.com/support-and-downloads/downloads"]

    def parse(self, response):
        script = ''.join(response.xpath("//div[@id='page_stuff']/script/text()").extract()).split('\"')

        for product in script:
            if ',' not in product and ' ' not in product:
                model = product.replace("\\", "")

                yield FormRequest.from_response(response,
                                                formname="form_downloads_search",
                                                formdata={"search_model_number": model},
                                                meta={"product": model},
                                                headers={"Referer": response.url, "X-Requested-With": "XMLHttpRequest"},
                                                callback=self.parse_product)

    def parse_product(self, response):
        json_response = json.loads(response.body_as_unicode())

        if json_response["success"]:
            for prod in json_response["product_downloads"]:
                product = json_response["product_downloads"][prod]
                for link in product.get("downloads", {}).get(
                        "69", {}).get("files", {}):

                    item = FirmwareLoader(item=FirmwareImage(),
                                          response=response,
                                          date_fmt=["%Y-%m-%d"])
                    item.add_value("version", link["version"])
                    item.add_value("date", link["date"])
                    item.add_value("description", link["notes"])
                    item.add_value("url", link["link_url"])
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
