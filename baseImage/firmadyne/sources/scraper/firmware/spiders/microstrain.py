from scrapy import Spider

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader


class MicrostrainSpider(Spider):
    name = "microstrain"
    allowed_domains = ["microstrain.com"]
    start_urls = ["http://www.microstrain.com/support"]

    # http://files.microstrain.com/8401-0006-Firmware-Upgrades-for-3DM-GX3.pdf

    firmware = ["http://files.microstrain.com/MicroStrain_Wireless_Firmware.zip",
                "http://download.microstrain.com/3DM-GX3-Upgrades/3DM-GX3-15_25_MIP_firmware_upgrade.zip",
                "http://download.microstrain.com/3DM-GX3-Upgrades/3DM-GX3-25_Single_Byte_firmware_upgrade.zip",
                "http://download.microstrain.com/3DM-GX3-Upgrades/3DM-GX3-35_MIP_firmware_upgrade.zip",
                "http://download.microstrain.com/3DM-GX3-Upgrades/3DM-GX3-45_MIP_firmware_upgrade.zip"]

    def parse(self, response):
        for url in self.firmware:
            item = FirmwareLoader(item=FirmwareImage())
            item.add_value("url", url)
            item.add_value("product", url.split("/")[-1].split("_")[0])
            item.add_value("vendor", self.name)
            yield item.load_item()
