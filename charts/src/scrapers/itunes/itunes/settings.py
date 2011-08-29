# Scrapy settings for itunes project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'itunes'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['itunes.spiders']
NEWSPIDER_MODULE = 'itunes.spiders'
DEFAULT_ITEM_CLASS = 'itunes.items.ItunesItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

HTTPCACHE_ENABLED = 1
HTTPCACHE_DIR = '/tmp/charts/scrapy'
HTTPCACHE_EXPIRATION_SECS = 7200


# itunes specific
OUTPUT_DIR = '/tmp/charts'
ITUNES_LIMIT = 100
ITUNES_EXPIRE = 7200
