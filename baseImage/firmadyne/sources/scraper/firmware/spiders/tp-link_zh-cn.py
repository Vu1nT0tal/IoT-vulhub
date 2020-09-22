# -*- coding: utf-8 -*

from scrapy import Spider
from scrapy.http import FormRequest

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

from urllib.parse import urljoin
import json
import re


class TPLinkZHSpider(Spider):
    name = "tp-link_zh-cn"
    vendor = "tp-link"
    allowed_domains = ["tp-link.com.cn"]
    start_urls = [
        "http://service.tp-link.com.cn/list_download_software_1_0.html"]

    def parse(self, response):
        script = response.css("script")[9].get()
        match = re.search(r'maxPage = "(\d+)"', script)
        if not match:
            return

        self.logger.debug(match.groups())
        maxPage = int(match[1])

        for page in range(1, maxPage+1):
            yield FormRequest(urljoin(response.url, '/download1/readmore'), method='GET', formdata={"ordertype": "0", "classtip": "software", "p": str(page)},
                              headers={"Referer": response.url},
                              callback=self.parse_json)

    def parse_json(self, response):
        resp = json.loads(response.text)
        self.logger.debug(resp)
        for product in resp:
            name = product['showName'].strip()
            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%Y%m%d"])

            # Model, Version, Date, Build
            self.logger.debug("Parsing '%s'" % name)
            match = re.search(
                r'^(.+) (V[\d\.]+)([^\d]+)(\d+)_([\d\.]+)$', name)

            if match:
                self.logger.debug(match.groups())
                item.add_value("product", match[1])
                item.add_value("version", match[2])
                date = match[4]
                if len(date) == 6:
                    date = "20" + date
                item.add_value("date", date)
                item.add_value("build", match[5])
            else:
                # TL-NVR5104 V1.0_171205.标准版
                match = re.search(
                    r'^(.+)[_ ]([vV][\d\.]+)([^\d]*)_([\d]+)([^\d]+)$', name)
                if match:
                    self.logger.debug(match.groups())
                    item.add_value("product", match[1])
                    item.add_value("version", match[2])
                    date = match[4]
                    if len(date) == 6:
                        date = "20" + date
                    item.add_value("date", date)
                    item.add_value("build", match[5])
                else:
                    # TL-IPC545K(P) V3.0_180227（1.0.14）标准版
                    match = re.search(
                        r'^(.+)[_ ](V[\d\.]+)_(\d+)（([\d\.]+)）([^\d]+)$', name)
                    if match:
                        self.logger.debug(match.groups())
                        item.add_value("product", match[1])
                        item.add_value("version", match[2])
                        date = match[3]
                        if len(date) == 6:
                            date = "20" + date
                        item.add_value("date", date)
                        item.add_value("build", match[4] + ' ' + match[5])
                    else:
                        self.logger.debug("No match for %s" %
                                          name)

            item.add_value("url", product['fileName'])
            item.add_value("description", name)
            item.add_value("vendor", self.vendor)
            yield item.load_item()
