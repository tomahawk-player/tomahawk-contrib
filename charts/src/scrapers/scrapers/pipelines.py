# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from time import gmtime, strftime
import shove
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

class ScrapersPipeline(object):

    def __init__(self):
        self.storage = None

    def open_spider(self, spider):
        self.storage = shove.Shove("file://"+settings['OUTPUT_DIR']+'/sources')


    def process_item(self, item, spider):

        if not item['id'] or len(item['id'].strip()) == 0:
            raise DropItem("Missing id: %s" % item)

        if not item['source'] or len(item['source'].strip()) == 0:
            raise DropItem("Missing source: %s" % item)

        source = item['source']
        chart_id = source+item['id']
        log.msg("Saving %s - %s" %(source, item['id']))

        list = self.storage.get(source, {})

        # metadata is the chart item minus the actual list plus a size
        metadata_keys = filter(lambda k: k != 'list', item.keys())
        metadata = { key: item[key] for key in metadata_keys }
        metadata['size'] = len(item['list'])
        metadata['date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        list[chart_id] = metadata
        self.storage[source] = list
        self.storage[chart_id] = dict(item)
        return item
