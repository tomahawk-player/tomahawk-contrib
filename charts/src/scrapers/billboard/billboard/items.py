# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import TakeFirst

class SingleItem(Item):
    track = Field(output_processor=TakeFirst())
    artist = Field(output_processor=TakeFirst())
    album = Field(output_processor=TakeFirst())
    rank = Field(output_processor=TakeFirst())

class ChartItem(Item):
    name = Field()
    id = Field()
    origin = Field()
    list = Field()
    genre = Field()
    type = Field()

class BillboardItem(ChartItem):
    pass
