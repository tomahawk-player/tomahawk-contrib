#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Casey Link <unnamedrambler@gmail.com>
# Copyright (C) 2012 Hugo Lindström <hugolm84@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import lxml.html
from lxml import etree
import urllib2
import json
import re
import hashlib
from urlparse import urlparse as urlparser

#
#scrapy modules
#
from scrapy.conf import settings
from scrapy import log
from scrapy.spider import BaseSpider
from scrapers.items import SingleTrackItem, SingleAlbumItem, ChartItem

from sources.utils import cache as chartCache

generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'

@chartCache.methodcache.cache('get_countries', expire=settings['ITUNES_EXPIRE'])
def get_countries():
    doc = lxml.html.parse(generator_url)
    countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]
    return countries

def get_genre(_id):
    return chartCache.storage['itunesgenre_'+_id]

def set_genre(_id, name):
    chartCache.storage['itunesgenre_'+_id] = name

def get_maxAge() :
    today = datetime.datetime.today()
    expires = datetime.datetime.replace(today +  datetime.timedelta(days=1),hour=1, minute=0, second=0)
    maxage = expires-today
    return maxage.seconds

#@chartCache.methodcache.cache('get_music_feeds', expire=settings['ITUNES_EXPIRE'])
def get_music_feeds(countries):
    # { name: country, charts: [], genres: [] }
    music_data = []
    for cc in countries:
        url = available_url % (cc)
        data = urllib2.urlopen(url).read()
        
        # the response has a jsonp callback, lets remove that
        data = data.replace("availableFeeds=", "")
        j = json.loads(data)
        # there are alot of categories, we just want the ones with music
        for cat in j['list']:
            if cat['name'] != "Music" :
                continue
            # returns a list of tuples, where each tuple
            # contains the genre name and numeric id
            genres = [ (g['value'], g['display'] ) for g in cat['genres']['list'] ]
            for g in genres:
                set_genre(g[0], g[1])
            
            # returns a list of tuples, where each tuple
            # contains:
            # url suffix (e.g., 'xml')
            # url prefix
            # name of the feed (e.g, "topalbums")
            # display name of the feed (e.g., "Top Albums")
            # cc is the country id
            charts = [ (c['urlSuffix'], c['urlPrefix'], c['name'], c['display']) for c in cat['types']['list'] ]
            music_data.append( { "country":c, "charts": charts, "genres": genres, "cc" : cc } )
    
    return music_data

def construct_feeds(music_feeds, limit):
    feeds = []
    for item in music_feeds:
        for chart in item['charts']:
            base_url = chart[1]
            suffix = chart[0]
            url = "%s/limit=%s/cc=%s/%s" % (base_url, limit, item['cc'], suffix)
            feeds.append(url)
            for genre in item['genres']:
                g_id = genre[0]
                if len(g_id.strip()) == 0:
                    #sometimes we get blank genres
                    continue
                url = "%s/limit=%s/genre=%s/cc=%s/%s" % (base_url, limit, g_id, item['cc'], suffix)
                feeds.append(url)
    # Only return US new releases
    return filter(lambda url: 'rss.xml' in url and "US" in url or 'rss.xml' not in url, feeds)

def get_feed_urls(limit):
    feeds = construct_feeds(get_music_feeds(get_countries()), limit)
    return feeds

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
        elif feed.tag == 'rss':
            return self.parse_rss(feed, response.url)
    
    # Itunes is weird, but that we know. There's sometimes no information about this feed
    # in the response, so we need to construct Title and so forth
    # Also, its sometimes b0rked description filled with bs json
    def parse_rss(self, feed, url):
        genre_name = None
        feed_extra = None
        feed_type = "Album"
        geo = None
        genre = filter(lambda k: 'genre' in k, urlparser(url).path.split("/"))
        try :
            genre_name = get_genre( genre[0].split("=")[1] )
            # geo in xpath is different ISO than in url. We want cc not xpath
            # geo = feed.xpath('.//channel/language')[0].text
            geo_re = re.compile("cc=(.*)(?=\/)")
            rGeo =  geo_re.search(url)
            if rGeo != None:
                geo = rGeo.groups()[0]
        except IndexError :
            return
        
        if 'newreleases' in url :
            feed_extra = "New Album Releases"
        if 'justadded' in url :
            feed_extra = "Just Added Albums"
        if 'featuredalbums' in url:
            feed_extra = "Featured Albums"
        
        if feed_extra is None or genre_name is None or geo is None :
            return
        
        ns = { 'itms': 'http://phobos.apple.com/rss/1.0/modules/itms/' }
        entries = feed.xpath('.//channel/item')
        rank = 0
        chart_list = []
        for entry in entries:
            artist = entry.xpath('itms:artist', namespaces=ns)[0].text
            album = entry.xpath('itms:album', namespaces=ns)[0].text
            rank += 1
            item = SingleAlbumItem()
            item['artist'] = artist
            item['album'] = album
            item['rank'] = rank
            chart_list.append( dict(item) )
        
        chart = ChartItem()
        # Unique ids
        _id = url
        md5 = hashlib.md5()
        md5.update(_id)
        _id = md5.hexdigest()
        
        chart['id'] = _id
        chart['origin'] = url
        chart['genre'] = genre_name
        chart['geo'] = geo.lower()
        chart['name'] = genre_name
        chart['extra'] = feed_extra
        chart['type'] = feed_type
        chart['list'] = chart_list
        chart['source'] = 'itunes'
        # maxage is the last item scraped
        cacheControl = chartCache.setCacheControl(get_maxAge())
        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")
        
        if _id == settings["ITUNES_DEFAULT_NRCHART"]:
            chart['default'] = 1
        
        return chart
    
    def parse_atom(self, feed):
        ns = {'ns': 'http://www.w3.org/2005/Atom',
            'im': 'http://itunes.apple.com/rss'}
        try:
            _id = feed.xpath('/ns:feed/ns:id', namespaces=ns)[0].text
            _type = feed.xpath('/ns:feed/ns:entry/im:contentType/im:contentType', namespaces=ns)[0].attrib['term']
        except IndexError:
            return

        if _type != "Album" and _type != "Track":
            return # skip playlists

        entries = feed.xpath('/ns:feed/ns:entry', namespaces=ns)
        chart_list = []
        rank = 0
        for entry in entries:
            title = entry.xpath('im:name', namespaces=ns)[0].text
            artist = entry.xpath('im:artist', namespaces=ns)[0].text
            if _type == "Album":
                album = title
                item = SingleAlbumItem()
            elif _type == "Track":
                album = entry.xpath('im:collection/im:name', namespaces=ns)[0].text
                item = SingleTrackItem()
                item['track'] = title
            
            rank += 1
            item['artist'] = artist
            item['album'] = album
            item['rank'] = rank
            chart_list.append( dict(item) )

        title = feed.xpath('ns:title', namespaces=ns)[0].text

        geo = None
        geo_re = re.compile("cc=([a-zA-Z]+)")
        rGeo =  geo_re.search(_id)
        if rGeo != None:
            geo = rGeo.groups()[0]

        genre = None
        genre_re = re.compile("genre=(\d+)/")
        rGenre =  genre_re.search(_id)
        if rGenre != None:
            genre = rGenre.groups()[0]

        if not genre is None:
            genre = get_genre(genre)

        origin = _id
        md5 = hashlib.md5()
        md5.update(_id)
        _id = md5.hexdigest()

        if geo is None:
            geo_s = origin.split("/")
            geo = geo_s

        chart = ChartItem()
        # Itunes expires tomorrow at 00am
        chart['id'] = _id
        chart['origin'] = origin
        chart['genre'] = genre
        chart['geo'] = geo
        chart['name'] = title
        chart['type'] = _type
        chart['list'] = chart_list
        chart['source'] = 'itunes'

        # maxage is the last item scraped
        cacheControl = chartCache.setCacheControl(get_maxAge())
        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")

        if(_id == settings["ITUNES_DEFAULT_ALBUMCHART"] or _id == settings["ITUNES_DEFAULT_TRACKCHART"]):
            chart['default'] = 1

        return chart