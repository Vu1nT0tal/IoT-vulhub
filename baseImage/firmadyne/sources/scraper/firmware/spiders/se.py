# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import logging
import urlparse

#from scrapy.shell import inspect_response #inspect_response(response, self)


class SchneiderElectricSpider(Spider):
    name = "se"
    allowed_domains = ["se.com"]
    start_urls = ("https://www.se.com/us/en/product-range-az",)

    def parse(self, response):
        a_to_z = response.css('ul.product-finder-result')
        for link in a_to_z.xpath('.//a'):
            product = u' '.join(link.xpath('.//text()').extract()).strip()
            href = link.xpath('@href').extract_first()

            yield Request(
                url=urlparse.urljoin(response.url, href),
                headers={"Referer": response.url},
                meta={'product': product},
                callback=self.parse_product)

    def parse_product(self, response):
        # Find the "Software and Firmware" tab link to get to the product-range-download page
        meta = response.meta
        meta['dont_redirect'] = True
        for link in response.css('a.tab-link'):
            href = link.xpath('@href').extract_first()
            if href.endswith(u'software-firmware-tab'):
                logging.debug("Requesting SW+FW page for %s at %s",
                        response.meta['product'], urlparse.urljoin(response.url, href))

                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    meta=meta,
                    callback=self.parse_product_sw_fw)

                break
        else:
            logging.debug("Did not find a 'Software and Firmware' tab for %s",
                    response.meta['product'])

    def parse_product_sw_fw(self, response):
        product = response.meta['product']
        fw_sect = None

        #inspect_response(response, self)
        col_selector_map = {}
        # Find the "Firmware" section.  NOTE: whitespace in the class is intentional
        for section in response.css('div.docs-table__section '):
            for col in section.css('div.docs-table__column-name'):
                col_text = col.xpath('.//text()').extract_first().strip()
                if len(col_text) > 1:
                    col_selector_map[col_text] = section
        try:
            fw_sect = col_selector_map[u'Firmware']
        except KeyError:
            logging.debug("Did not find a 'Firmware' section in the downloads for %s", product)
            return

        # Iterate Firmware rows
        for fw_row in fw_sect.css('div.docs-table__row'):
            fw_version, fw_href, fw_date, fw_desc = self.extract_fw_info(fw_row, response)
            if fw_href is None:
                continue

            item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%m/%d/%y"])
            item.add_value('product', product)
            item.add_value('vendor', self.name)
            item.add_value('url', fw_href)
            item.add_value('description', fw_desc)
            item.add_value('date', fw_date)
            yield item.load_item()

    def extract_fw_info(self, fw_row, response=None):
        # Throw away known non-firmware files.  Keep archive files that contain release notes.
        '''
        file_type = u' '.join(fw_row.css('div.docs-table__column-format *::text').extract()).rstrip()
        logging.debug("File Type: %s for %s", file_type, response.url)
        if any(file_type.endswith(x) for x in (u'pdf',)):
            ret = (None, None, None, None)
            return ret
        '''

        # Firmware link
        #  The tool-tip links sometimes allows for separate fw-only download, but it is inconsistent
        #  Throw away '.pdf', '.pdf.7z', '.pdf.zip' files
        fw_name_col = fw_row.css('div.docs-table__column-name')
        fw_href = fw_name_col.xpath('.//a/@href').extract_first()
        if any(fw_href.find(x) != -1 for x in (u'.pdf', )):
            logging.debug("Ignoring firmware link because it contained '.pdf': %s", fw_href)
            return (None, None, None, None)

        # Firmware version
        try:
            fw_version = fw_name_col.xpath('.//a/text()').re(ur'.*\s+\(Version\s+(.+)\)')[0]
        except IndexError:
            fw_version = None
            # logging.debug("Failed to extract version from '%s'",
            #        fw_name_col.xpath('.//text()').extract())

        # Firmware date
        date_select = fw_row.css('div.docs-table__column-date *::text')
        # NOTE: This didn't work for https://www.se.com/us/en/product-range-download/62130-modicon-m251-micro-plc-with-dual-channel-comm./
        #  Got 00/24/18 when it should have been 10/24/18 
        #  Left this in case someone wanted to debug
        # try:
        #    fw_date_orig = date_select.re(ur'.*([1]?\d{1}/[1-3]?\d{1}/\d{1,2}).*')[0]
        #except IndexError:
        #    logging.debug("Did not fid date in %s", date_select.extract())
        #    fw_date_orig = ''
        fw_date_orig = u' '.join(date_select.extract()).rstrip().split(u' ')[-1]
        fw_date_list = fw_date_orig.split(u'/')
        for k, v in enumerate(fw_date_list):
            if len(v) < 2:
                fw_date_list[k] = u"0"+v
        fw_date = u'/'.join(fw_date_list)
        # logging.debug("Extracted Date: %s Converted Date: %s for %s",
        #        fw_date_orig, fw_date, response.url)

        # Firmware details
        fw_tooltip_desc = fw_row.css('div.tooltip-body__text')
        fw_desc = fw_tooltip_desc.xpath('.//text()').extract_first() if fw_tooltip_desc else None
        ret = (fw_version, fw_href, fw_date, fw_desc)
        # logging.debug("returning: %s", ret)
        return ret
