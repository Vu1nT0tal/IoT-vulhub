from scrapy import Spider
from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class Tenvispider(Spider):
    name = "tenvis"
    allowed_domains = ["tenvis.com"]
    start_urls = ["http://forum.tenvis.com/viewtopic.php?f=13&t=3233"]

    # from the image
    # http://forum.tenvis.com/download/file.php?id=6163&sid=cfffb0412651f05728623840e8fc5584&mode=view
    firmware = [("JPT3815W, JPT3815W+", "0.22.2.34"),
                ("JPT3815W, JPT3815W+", "0.37.2.36"),
                ("JPT3815W, JPT3815W+", "32.37.2.39"),
                ("JPT3815W, JPT3815W+", "1.7.25"),
                ("JPT3815W, JPT3815W+", "1.7.25"),
                ("JPT3815W, JPT3815W+", "1.7.25"),
                ("JPT3815W, JPT3815W+", None),
                ("JPT3815W, JPT3815W+", None),
                ("JPT3815W P2P, TR3818/TR3828", "3.1.1.1.4"),
                ("ROBOT2", "0.22.2.34"),
                ("ROBOT2", "0.37.2.36"),
                ("ROBOT2", "32.37.2.39"),
                ("ROBOT2", "3.1.1.1.4"),
                ("391W", "0.22.2.34"),
                ("391W", "0.37.2.36"),
                ("391W", "32.37.2.39"),
                ("391W", "3.7.25"),
                ("391W", "3.7.25"),
                ("391W", "5.1.1.1.5"),
                ("602W", "0.22.2.34"),
                ("602W", "0.37.2.36"),
                ("602W", "32.37.2.39"),
                ("602W", "3.7.25"),
                ("602W", "3.7.25"),
                ("602W", "5.1.1.1.5"),
                ("MINI319", "0.22.2.34"),
                ("MINI319", "0.37.2.36"),
                ("MINI319", "32.37.2.39"),
                ("MINI319", "2.7.25"),
                ("MINI319", "2.7.25"),
                ("MINI319", "2.7.25"),
                ("MINI319", "12.1.1.1.2"),
                ("ROBOT3", "1.3.3.3"),
                ("ROBOT3", "1.2.7.2"),
                ("ROBOT3", "1.2.1.4"),
                ("ROBOT3", "7.1.1.1.1.2"),
                ("ROBOT3", None),
                ("391W HD", "1.3.3.3"),
                ("391W HD", "1.2.7.2"),
                ("TH671", "8.1.1.1.1.2"),
                ("TH692", None),
                ("TH661", "7.1.1.1.1.2"),
                ("TH661", None),
                ("JPT3815W HD", None),
                ("JPT3815W HD", None)]

    def parse(self, response):
        for entry in response.xpath("//div[@class='content']//a"):
            text = entry.xpath(".//text()").extract()
            href = entry.xpath("./@href").extract()[0]

            idx = None
            for string in text:
                if "---" in string:
                    idx = int(string.split("-")[0])
                    break

            if not idx:
                continue

            item = FirmwareLoader(item=FirmwareImage(), response=response)
            item.add_value("url", href)
            item.add_value("version", self.firmware[idx][1])
            item.add_value("product", self.firmware[idx][0])
            item.add_value("vendor", self.name)
            yield item.load_item()
