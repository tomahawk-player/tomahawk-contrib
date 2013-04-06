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

class SingleTrackItem(Item):
    track = Field(input_processor=Strip(), output_processor=TakeFirst())
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    album = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())

class SingleUrlTrackItem(Item):
    track = Field(input_processor=Strip(), output_processor=TakeFirst())
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    stream_url = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())

class SingleUrlAlbumItem(Item):
    album = Field(input_processor=Strip(), output_processor=TakeFirst())
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    url = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())

class SingleAlbumItem(Item):
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    album = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())

class SingleArtistItem(Item):
    artist = Field(input_processor=Strip(), output_processor=TakeFirst())
    rank = Field(input_processor=Strip(), output_processor=TakeFirst())


class Detail():
    def __init__(self, id, name = None, description = None, have_extra = False ):
        if not name :
            name = self.__titlecase__(id)
        self.__detail = {'id' : id,
            'name' : name,
            'description' : description,
            'image' : "http://hatchet.is/images/%s-logo.png" % slugify(id),
            'have_extra' : have_extra
        }

    def __titlecase__(self, s):
        return re.sub(r"[A-Za-z]+(['.][A-Za-z]+)?",
               lambda mo: mo.group(0)[0].upper() +
                          mo.group(0)[1:].lower(),
               s)

    def __getattr__(self, name, *args) :
        return getattr(self.__detail, name);

class DetailItem(Item):
    id = Field()
    name = Field()
    description = Field()
    image = Field()
    have_extra = Field()

class ChartItem(Item):
    name = Field()
    display_name = Field()
    id = Field()
    origin = Field()
    list = Field()
    genre = Field()
    type = Field()
    geo = Field()
    source = Field()
    default = Field()
    date = Field()
    expires = Field()
    maxage = Field()
    extra = Field()

class ScrapersItem(ChartItem):
    pass
