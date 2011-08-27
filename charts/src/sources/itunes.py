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
import json
import urllib2
import string

#local includes
import utils
from utils.cache import cache
from utils import feed_fetcher


COUNTRY_EXPIRE = 86400 # i day
FEED_LIST_EXPIRE = 86400

generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'


#######################################################################
# Fetch and Construct Feed List
#
# This section parses the iTunes generator page and constructs a list of
# every possible data feed for Music

@cache.cache('get_countries', expire=COUNTRY_EXPIRE)
def get_countries():
    doc = lxml.html.parse(generator_url)

    countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]

    return countries


@cache.cache('get_music_feeds', expire=FEED_LIST_EXPIRE)
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


def fetch(urls):
    feed_fetcher.start_job(urls[0:2])


def main():
    fetch(get_feed_urls(10))

if __name__ == '__main__':
    main()
