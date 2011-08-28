# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class SingleItem(Item):
    track = Field()
    artist = Field()
    album = Field()
    rank = Field()
    visit_id = Field()
    visit_status = Field()

class ChartItem(Item):
    visit_id = Field()
    visit_status = Field()
    name = Field()
    id = Field()
    origin = Field()
    list = Field()
    genre = Field()
    type = Field()

class BillboardItem(ChartItem):
    pass
