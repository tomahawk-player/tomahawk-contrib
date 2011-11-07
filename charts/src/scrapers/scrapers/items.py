# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import TakeFirst
import re

class Strip(object):
    def __call__(self, values):
        return [ v.strip() for v in values ]

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

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
    default = Field()
    date = Field()
class ScrapersItem(ChartItem):
    pass
