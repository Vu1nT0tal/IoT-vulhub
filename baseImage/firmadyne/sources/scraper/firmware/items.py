from scrapy.item import Item, Field

class FirmwareImage(Item):
    product = Field(default=None)
    vendor = Field()

    description = Field(default=None)
    version = Field(default=None)
    build = Field(default=None)
    date = Field(default=None)

    mib = Field(default=None)
    sdk = Field(default=None)
    url = Field()

    # used by FilesPipeline
    files = Field()
    file_urls = Field()
