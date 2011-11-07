from time import gmtime, strftime
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import lxml.html
from lxml import etree
import urllib2
import json
import re
import hashlib
import shove

#
#scrapy modules
#
from scrapy.conf import settings
from scrapy import log
from scrapy.spider import BaseSpider
from scrapers.items import SingleItem, ChartItem

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': settings['OUTPUT_DIR']+'/cache/data',
    'cache.lock_dir': settings['OUTPUT_DIR']+'/cache/lock'
}

methodcache = CacheManager(**parse_cache_config_options(cache_opts))
storage = shove.Shove('file://'+settings['OUTPUT_DIR']+'/sources')
generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'

@methodcache.cache('get_countries', expire=settings['ITUNES_EXPIRE'])
def get_countries():
    doc = lxml.html.parse(generator_url)

    countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]

    return countries

def get_genre(id):
    return storage['itunesgenre_'+id]

def set_genre(id, name):
    storage['itunesgenre_'+id] = name


@methodcache.cache('get_music_feeds', expire=settings['ITUNES_EXPIRE'])
def get_music_feeds(countries):
    # { name: country, charts: [], genres: [] }
    music_data = []

    for c in countries:
        url = available_url % (c)

        data = urllib2.urlopen(url).read()

        # the response has a jsonp callback, lets remove that
        data = data.replace("availableFeeds=", "")

        j = json.loads(data)
        # there are alot of categories, we just want the ones with music
        for type in j['list']:
            if type['name'] != "Music":
                continue
            # returns a list of tuples, where each tuple
            # contains the genre name and numeric id
            genres = [ (g['value'], g['display'] ) for g in type['genres']['list'] ]
            for g in genres:
                set_genre(g[0], g[1])

            # returns a list of tuples, where each tuple
            # contains:
            # url suffix (e.g., 'xml')
            # urk prefix
            # name of the feed (e.g, "topalbums")
            # display name of the feed (e.g., "Top Albums")
            charts = [ (c['urlSuffix'], c['urlPrefix'], c['name'], c['display']) for c in type['types']['list'] ]

            music_data.append( { "country":c, "charts": charts, "genres": genres } )

    return music_data

def construct_feeds(music_feeds, limit):
    feeds = []
    for item in music_feeds:
        country = item['country']
        for chart in item['charts']:
            base_url = chart[1]
            suffix = chart[0]
            url = "%s/limit=%s/%s" % (base_url, limit, suffix)
            feeds.append(url)
            for genre in item['genres']:
                g_id = genre[0]
                if len(g_id.strip()) == 0:
                    #sometimes we get blank genres
                    continue
                url = "%s/limit=%s/genre=%s/%s" % (base_url, limit, g_id, suffix)
                feeds.append(url)
    return feeds

def get_feed_urls(limit, rss = False):
    feeds = construct_feeds(get_music_feeds(get_countries()), limit)
    if rss:
        return feeds
    return filter(lambda url: not 'rss.xml' in url, feeds)

class ItunesSpider(BaseSpider):
    name = 'itunes.com'
    allowed_domains = ['itunes.com']
    start_urls = get_feed_urls(settings['ITUNES_LIMIT'])

    def parse(self, response):
        try:
            feed = etree.fromstring(response.body)
        except etree.XMLSyntaxError:
            log.msg("Parse error, skipping: %s"%(response.url), loglevel=log.WARNING)
            return None

        if feed.tag == '{http://www.w3.org/2005/Atom}feed':
            return self.parse_atom(feed)
        #elif feed.tag == 'rss':
            #return process_rss(feed)
            #return # TODO finish rss parsing

    def parse_atom(self, feed):
        ns = {'ns': 'http://www.w3.org/2005/Atom',
              'im': 'http://itunes.apple.com/rss'}
              
        try:
          id = feed.xpath('/ns:feed/ns:id', namespaces=ns)[0].text
          type = feed.xpath('/ns:feed/ns:entry/im:contentType/im:contentType', namespaces=ns)[0].attrib['term']
        except IndexError, e:
          return
          
        if type != "Album" and type != "Track":
            return # skip playlists
        i = 1
        entries = feed.xpath('/ns:feed/ns:entry', namespaces=ns)
        list = []
        for entry in entries:
            title = entry.xpath('im:name', namespaces=ns)[0].text
            artist = entry.xpath('im:artist', namespaces=ns)[0].text
            if type == "Album":
                album = title
                track = ''
            elif type == "Track":
                track = title
                album = entry.xpath('im:collection/im:name', namespaces=ns)[0].text
            rank = i
            i += 1
            item = SingleItem()
            item['artist'] = artist
            item['track'] = track
            item['album'] = album
            item['rank'] = rank
            list.append( dict(item) )

        title = feed.xpath('ns:title', namespaces=ns)[0].text
        geo = None
        geo_re = re.compile("cc=(.*)")
        r =  geo_re.search(id)
        if r != None:
           geo = r.groups()[0]

        genre = None
        genre_re = re.compile("genre=(\d+)/")
        r =  genre_re.search(id)
        if r != None:
            genre = r.groups()[0]

        if not genre is None:
            genre = get_genre(genre)

        origin = id
        md5 = hashlib.md5()
        md5.update(id)
        id = md5.hexdigest()

        if geo is None:
           geo_s = origin.split("/")
           geo = geo_s


        chart = ChartItem()
        chart['id'] = id
        chart['origin'] = origin
        chart['genre'] = genre
        if(geo[3]):
           chart['geo'] = geo[3]
        else:
           chart['geo'] = geo
        chart['name'] = title
        chart['type'] = type
        chart['list'] = list
        chart['date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        chart['source'] = 'itunes'
        if(id == settings["ITUNES_DEFAULT_ALBUMCHART"] or id == settings["ITUNES_DEFAULT_TRACKCHART"]):
           chart['default'] = 1

        return chart
