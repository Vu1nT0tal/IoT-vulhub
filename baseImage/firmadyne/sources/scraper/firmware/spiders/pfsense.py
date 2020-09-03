from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import os
import urlparse


class PfSenseSpider(Spider):
    name = "pfsense"
    allowed_domains = ["pfsense.org"]
    start_urls = ["http://files.pfsense.org/mirror/downloads/"]

    def parse(self, response):
        for link in response.xpath("//a"):
            text = link.xpath(".//text()").extract()[0]
            href = link.xpath(".//@href").extract()[0]

            if ".." in href:
                continue
            elif href.endswith('/'):
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    callback=self.parse)
            elif href.endswith(".gz") and ".iso" not in href:
                # strip off multiple file extensions
                basename = os.path.splitext(text)[0]
                while ".img" in basename or ".iso" in basename:
                    basename = os.path.splitext(basename)[0]

                basename = basename.split("-")
                version = FirmwareLoader.find_version_period(basename)

                # attempt to parse filename and generate product/version
                # strings
                remove = [version] if version else []
                for i in range(0, len(basename)):
                    if "BETA" in basename[i]:
                        version += "-%s%s" % (basename[i], basename[i + 1])
                        remove.append(basename[i])
                        remove.append(basename[i + 1])
                    elif "RC" in basename[i]:
                        version += "-%s" % (basename[i])
                        remove.append(basename[i])
                    elif "RELEASE" in basename[i]:
                        remove.append(basename[i])

                basename = [x for x in basename if x not in remove]

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                item.add_value("version", version)
                item.add_value("url", href)
                item.add_value("date", item.find_date(
                    link.xpath("following::text()").extract()))
                item.add_value("product", "-".join(basename))
                item.add_value("vendor", self.name)
                yield item.load_item()
