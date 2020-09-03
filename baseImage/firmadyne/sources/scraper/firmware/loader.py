from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst

import datetime
import re
import string
import urlparse


class FirmwareLoader(ItemLoader):

    @staticmethod
    def find_product(text):
        match = re.search(r"(?:model[:. #]*([\w-][\w.-]+))", " ".join(
            text).replace(u"\xa0", " ").strip(), flags=re.IGNORECASE)
        return next((x for x in match.groups() if x), None) if match else None

    @staticmethod
    def find_version(text):
        match = re.search(r"(?:version[:. ]*([\w-][\w.-]+)|ve?r?s?i?o?n?[:. ]*([\d-][\w.-]+))",
                          " ".join(text).replace(u"\xa0", " ").strip(), flags=re.IGNORECASE)
        return next((x for x in match.groups() if x), None) if match else None

    @staticmethod
    def find_build(text):
        match = re.search(r"(?:build[:. ]*([\w-][\w.-]+)|bu?i?l?d?[:. ]*([\d-][\w.-]+))",
                          " ".join(text).replace(u"\xa0", " ").strip(), flags=re.IGNORECASE)
        return next((x for x in match.groups() if x), None) if match else None

    @staticmethod
    def find_version_period(text):
        match = re.search(r"((?:[0-9])(?:[\w-]*\.[\w-]*)+)",
                          " ".join(text).replace(u"\xa0", " ").strip())
        return next((x for x in match.groups() if x and "192.168." not in x.lower()), None) if match else None

    def find_date(self, text):
        for fmt in self.context.get("date_fmt", []):
            fmt = "(" + re.escape(fmt).replace("\%b", "[a-zA-Z]{3}").replace("\%B", "[a-zA-Z]+").replace(
                "\%m", "\d{1,2}").replace("\%d", "\d{1,2}").replace("\%y", "\d{2}").replace("\%Y", "\d{4}") + ")"
            match = re.search(fmt, "".join(text).strip())
            res = filter(lambda x: x, match.groups()) if match else None

            if res:
                return res[0]
        return None

    def clean(s):
        return filter(lambda x: x in string.printable, s).replace("\r", "").replace("\n", "").replace(u"\xa0", " ").strip()

    def fix_url(url, loader_context):
        if not urlparse.urlparse(url).netloc:
            return urlparse.urljoin(loader_context.get("response").url, url)
        return url

    def parse_date(date, loader_context):
        for fmt in loader_context.get("date_fmt", []):
            try:
                return datetime.datetime.strptime(date, fmt)
            except ValueError:
                pass
        return None

    def remove_html(s):
        return re.sub(r"<[a-zA-Z0-9\"/=: ]+>", "", s)

    default_output_processor = TakeFirst()

    product_in = MapCompose(clean)
    vendor_in = Identity()

    description_in = MapCompose(remove_html, clean)
    version_in = MapCompose(clean)
    build_in = MapCompose(clean)
    date_in = MapCompose(clean, parse_date)

    mib_in = MapCompose(fix_url)
    sdk_in = MapCompose(fix_url)
    url_in = MapCompose(fix_url)
