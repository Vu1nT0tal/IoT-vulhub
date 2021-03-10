from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import os
import urlparse


class SynologySpider(Spider):
    name = "synology"
    allowed_domains = ["synology.com"]
    start_urls = ["http://dedl.synology.com/download/DSM/beta/",
                  "http://dedl.synology.com/download/DSM/release/", "http://dedl.synology.com/download/VSFirmware/"]

    def parse(self, response):
        for entry in response.xpath("//table/tr[position() > 3]"):
            if not entry.xpath("./td[2]/a"):
                continue

            text = entry.xpath("./td[2]/a//text()").extract()[0]
            href = entry.xpath("./td[2]/a/@href").extract()[0]
            date = entry.xpath("./td[3]//text()").extract()[0]

            if "DSM" in response.url:
                if href.endswith('/'):
                    build = None
                    version = response.meta.get(
                        "version", FirmwareLoader.find_version_period([text]))
                    if not FirmwareLoader.find_version_period([text]):
                        build = text[0: -1]

                    yield Request(
                        url=urlparse.urljoin(response.url, href),
                        headers={"Referer": response.url},
                        meta={"build": build, "version": version},
                        callback=self.parse)
                elif all(not href.lower().endswith(x) for x in [".txt", ".md5", ".torrent"]):
                    product = None
                    basename = os.path.splitext(text)[0].split("_")

                    if "DSM" in basename:
                        if response.meta["build"] in basename:
                            basename.remove(response.meta["build"])
                        basename.remove("DSM")
                        product = " ".join(basename)
                    else:
                        product = basename[-2]

                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                    item.add_value("build", response.meta["build"])
                    item.add_value("version", response.meta["version"])
                    item.add_value(
                        "mib", "http://dedl.synology.com/download/Document/MIBGuide/Synology_MIB_File.zip")
                    item.add_value("url", href)
                    item.add_value("date", date)
                    item.add_value("product", product)
                    item.add_value("vendor", self.name)
                    yield item.load_item()
            elif "VSFirmware" in response.url:
                if href.endswith('/'):
                    version, build = text[0: -1].split("-")

                    yield Request(
                        url=urlparse.urljoin(response.url, href),
                        headers={"Referer": response.url},
                        meta={"build": build, "version": version},
                        callback=self.parse)
                elif all(not href.lower().endswith(x) for x in [".txt", ".md5", ".torrent"]):
                    basename = os.path.splitext(text)[0].split("_")

                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                    item.add_value("build", response.meta["build"])
                    item.add_value("version", response.meta["version"])
                    item.add_value("url", href)
                    item.add_value("date", date)
                    item.add_value("product", basename[0])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
