# Scrapy settings for scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os

try:
    BASEDIR = os.environ['OUTPUT_DIR']
except KeyError:
    BASEDIR = '/home/charts/cache'

SPIDER_MODULES = ['scrapers.spiders']
NEWSPIDER_MODULE = 'scrapers.spiders'
DEFAULT_ITEM_CLASS = 'scrapers.items.ScrapersItem'
LOG_LEVEL = 'INFO'
HTTPCACHE_ENABLED = 1
HTTPCACHE_DIR = BASEDIR + '/scrapy'
HTTPCACHE_EXPIRATION_SECS = 7200

ITEM_PIPELINES = [ 'scrapers.pipelines.ScrapersPipeline' ]

OUTPUT_DIR = BASEDIR


# billboard specific
BILLBOARD_DEFAULT_ALBUMCHART = "billboard-200"
BILLBOARD_DEFAULT_TRACKCHART = "hot-100"
# itunes specific
ITUNES_LIMIT = 100
ITUNES_EXPIRE = 7200
ITUNES_DEFAULT_ALBUMCHART = "c75e7d6473dac6829c3ea76fa3ba9ffb"
ITUNES_DEFAULT_TRACKCHART = "dc22ebfc4155404ec10afb436c3eb035"
ITUNES_DEFAULT_NRCHART = "084b7063d1914bf4393c3502691b4ace" # ALternative US Featured
ITUNES_DEFAULT_COUNTRY = "us"

GLOBAL_SETTINGS = {'OUTPUT_DIR': OUTPUT_DIR, 'EXPIRE' : 86400} # One day
