#!/usr/bin/env python
# Copyright (C) 2011 Casey Link <unnamedrambler@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import lxml.html
from lxml import etree
import json
import urllib2
import string
import re
import hashlib

#local includes
from utils import cache
from utils import url_fetcher
from source import Source


COUNTRY_EXPIRE = 86400 # 1 day
FEED_LIST_EXPIRE = 86400

generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'


#######################################################################
# Fetch and Construct Feed List
#
# This section parses the iTunes generator page and constructs a list of
# every possible data feed for Music

@cache.methodcache.cache('get_countries', expire=COUNTRY_EXPIRE)
def get_countries():
    doc = lxml.html.parse(generator_url)

    countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]

    return countries


@cache.methodcache.cache('get_music_feeds', expire=FEED_LIST_EXPIRE)
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
            stored_genres = cache.itunesstorage.get('genres', {})
            for g in genres:
                stored_genres[g[0]] = g[1]
            cache.itunesstorage['genres'] = stored_genres

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

def get_feed_urls(limit):
    feeds = construct_feeds(get_music_feeds(get_countries()), limit)
    return feeds



#######################################################################
# Fetch Feeds
#
# Use the feed urls constructed previously and fetch them using our
# fancy feed fetcher.

def wrap_metadata(name, source, type, geo, genre, id, origin, size):
    return locals()

def wrap_chart(name, source, list, type, geo, genre, id, origin):
    return locals()

def wrap_entry(rank, track, artist, album):
    #return {'rank': rank, 'track': track, 'artist': artist, 'album': album}
    return locals()

def itunes_process(resp, content):
    if resp.fromcache:
        # don't update
        print "got cache hit"
    if resp.status != 200:
        print "Error itunes response: " % (resp.status)
        return
    list = []

    feed = etree.fromstring(content)
    ns = {'ns': 'http://www.w3.org/2005/Atom',
          'im': 'http://itunes.apple.com/rss'}

    id = feed.xpath('/ns:feed/ns:id', namespaces=ns)[0].text
    type = feed.xpath('/ns:feed/ns:entry/im:contentType/im:contentType', namespaces=ns)[0].attrib['term']
    i = 1
    entries = feed.xpath('/ns:feed/ns:entry', namespaces=ns)
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
        list.append(wrap_entry(rank, track, artist, album))

    title = feed.xpath('ns:title', namespaces=ns)[0].text
    geo = None
    geo_re = re.compile("cc=(.*)")
    r =  geo_re.search(id)
    geo = r.groups()[0]

    genre = None
    genre_re = re.compile("genre=(\d+)/")
    r =  genre_re.search(id)
    if r != None:
        genre = r.groups()[0]

    if not genre is None:
        genres = cache.itunesstorage['genres']
        genre = genres[genre]

    origin = id
    md5 = hashlib.md5()
    md5.update(id)
    id = md5.hexdigest()
    chart  = wrap_chart(title, 'itunes', list, type, geo, genre, id, origin)
    metadata = wrap_metadata(title, 'itunes', type, geo, genre, id, origin, len(list))

    cache.itunesstorage[id] = chart
    list = cache.itunesstorage.get('itunes', {})
    list[id] = metadata
    cache.itunesstorage['itunes'] = list

def fetch(urls):
    url_fetcher.start_job(urls, itunes_process)

def test():
    fetch( get_feed_urls(10)[0:10] )
    list  = cache.itunesstorage.get('itunes')
    for id in list.keys():
        chart = cache.itunesstorage[id]
        print chart

class iTunesSource(Source):

    def __init__(self):
        return

    def chart_list(self):
        return cache.itunesstorage.get('itunes')

    def get_chart(self, url):
        return cache.itunesstorage.get(url, None)


def main():
    fetch(get_feed_urls(10))

if __name__ == '__main__':
    main()
