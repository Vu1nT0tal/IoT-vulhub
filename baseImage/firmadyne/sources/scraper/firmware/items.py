from scrapy.item import Item, Field

class FirmwareImage(Item):
    category = Field(default=None)
    vendor = Field()
    product = Field(default=None)

    description = Field(default=None)
    version = Field(default=None)
    build = Field(default=None)
    date = Field(default=None)

    size = Field(default=None)
    language = Field(default=None)

    mib = Field(default=None)
    sdk = Field(default=None)
    url = Field()

    # used by FilesPipeline
    files = Field()
    file_urls = Field()
