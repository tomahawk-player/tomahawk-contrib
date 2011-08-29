# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import TakeFirst

class Strip(object):
    def __call__(self, values):
        return [ v.strip() for v in values ]

class SingleItem(Item):
    track = Field(input_processor=Strip(), output_processor=TakeFirst())
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    album = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())

class ChartItem(Item):
    name = Field()
    id = Field()
    origin = Field()
    list = Field()
    genre = Field()
    type = Field()
    geo = Field()
    source = Field()

class ScrapersItem(ChartItem):
    pass
