# Scrapy settings for billboard project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'billboard'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['billboard.spiders']
NEWSPIDER_MODULE = 'billboard.spiders'
DEFAULT_ITEM_CLASS = 'billboard.items.BillboardItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
HTTPCACHE_ENABLED = 1
HTTPCACHE_DIR = '/tmp/charts/scrapy'
HTTPCACHE_EXPIRATION_SECS = 7200

#SPIDER_MIDDLEWARES = { 'project.middlewares.ignore.IgnoreVisitedItems': 560 }

