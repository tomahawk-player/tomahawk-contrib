# Scrapy settings for scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
BOT_NAME = 'scrapers'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scrapers.spiders']
NEWSPIDER_MODULE = 'scrapers.spiders'
DEFAULT_ITEM_CLASS = 'scrapers.items.ScrapersItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

HTTPCACHE_ENABLED = 1
HTTPCACHE_DIR = '/tmp/charts/scrapy'
HTTPCACHE_EXPIRATION_SECS = 7200

ITEM_PIPELINES = [ 'scrapers.pipelines.ScrapersPipeline' ]

OUTPUT_DIR = '/tmp/charts'

# itunes specific
ITUNES_LIMIT = 100
ITUNES_EXPIRE = 7200
