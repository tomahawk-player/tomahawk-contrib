# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy import log
import datetime
from sources.utils import cache as chartCache

class ScrapersPipeline(object):

    def __init__(self):
        self.storage = None

    def open_spider(self, spider):
        self.storage = chartCache.storage
        return

    def process_item(self, item, spider):

        if not item['id'] or len(item['id'].strip()) == 0:
            raise DropItem("Missing id: %s" % item)

        if not item['source'] or len(item['source'].strip()) == 0:
            raise DropItem("Missing source: %s" % item)

        source = item['source']
        # This is a little hack, for now, we only get new releases from Itunes
        # and its identified by extra field
        try :
            if source == "itunes" and item['extra'] :
                self.storage = chartCache.newreleases
            else : self.storage = chartCache.storage
        except :
            self.storage = chartCache.storage
        
        chart_id = source+item['id']
        log.msg("Saving %s - %s" %(source, item['id']))

        chart_list = self.storage.get(source, {})

        # metadata is the chart item minus the actual list plus a size
        metadata_keys = filter(lambda k: k != 'list', item.keys())
        metadata = { key: item[key] for key in metadata_keys }
        metadata['size'] = len(item['list'])
        chart_list[chart_id] = metadata
        self.storage[source] = chart_list
        self.storage[chart_id] = dict(item)
        self.storage[source+"cacheControl"] = dict(chartCache.setCacheControl(item["maxage"]))
        return item
