# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import logging
import json
import urllib.request, urllib.parse, urllib.error

# from scrapy.shell import inspect_response #inspect_response(response, self)


class QNAPSpider(Spider):
    name = "qnap"
    allowed_domains = ["qnap.com"]
    # start_urls = ("https://www.qnap.com/en/download",)
    start_urls = ("https://www.qnap.com/api/v1/download/models?locale_set=en", )

    jq_locale = "en"
    # qfile_api = "/api/v1/download/files?model_id={}&locale_set={}"
    # qmodel_api = "/api/v1/download/models?locale_set={}"
    qmodel_data = {}
    qdl_data = {}

    def parse(self, response):
        self.qmodel_data = json.loads(response.xpath('//p/text()').extract_first())["modelList"]
        for qmodel in self.qmodel_data:
            modelID = qmodel['modelID']
            file_uri = "https://qnap.com/api/v1/download/files?model_id={}&locale_set={}".format(modelID, self.jq_locale)
            yield Request(
                url=file_uri,
                headers={"Referer": response.url},
                meta=qmodel,
                callback=self.parse_model_files)

    def parse_model_files(self, response):
        meta = response.meta

        # Due to Python2 and unicode objects, we're using response body here.  Issues are from the 'remarks' fields.
        try:
            model_files = json.loads(response.body)['downloads']['firmware']
        except KeyError:
            logging.info("No downloadable firmware for %s", meta)
            return

        for _, fw_info in list(model_files.items()):
            href = fw_info['links']['global']  # options: {'global', 'europe', 'usa'}
            if not href.startswith("https://") and not href.startswith("http://"):
                href = urllib.urljoin("https://", href)

            item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt="%Y-%m-%d")
            item.add_value('product', meta['name'])
            item.add_value('vendor', self.name)
            item.add_value('description', fw_info['releasenote'])
            item.add_value('date', fw_info['published_at'])
            item.add_value('version', fw_info['version'])
            item.add_value('url', href)
            yield item.load_item()
