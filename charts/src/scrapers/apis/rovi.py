#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Casey Link <unnamedrambler@gmail.com>
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

from time import gmtime, strftime, time
import datetime
from operator import itemgetter
import urllib, urllib2
import md5
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import json
import shove
import sys
sys.path.append('../scrapers')
import settings
from items import ChartItem, SingleItem, slugify

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/cache/data',
    'cache.lock_dir': settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/cache/lock'
}

methodcache = CacheManager(**parse_cache_config_options(cache_opts))
newrelease_store = shove.Shove('file://'+settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/newreleases')

API_URI = "http://api.rovicorp.com/"
KEY = "7jxr9zggt45h6rg2n4ss3mrj"
SECRET = "XUnYutaAW6"
DAYS_AGO = 60
MAX_ALBUMS = 30
SOURCE = "rovi"

def make_sig():
    pre_sig = KEY+SECRET+str(int(time()))
    m = md5.new()
    m.update(pre_sig)
    return m.hexdigest()

def sign_args(args):
    args['apikey'] = KEY
    args['sig'] = make_sig()
    return args

def request(method, args):
    args = sign_args(args);
    url = "%s%s?%s" % (API_URI, method, urllib.urlencode(args))
    print("fetching: " + url)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    content = the_page.decode('utf-8')
    return json.loads(content)

@methodcache.cache('fetch_genres', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def fetch_genres():
    method = "data/v1/descriptor/musicgenres"
    args = {
        "country": "US",
        "format": "json",
        "language": "en"
    }
    j = request(method, args)
    try:
        if j['status'].strip() != "ok":
            return None
    except KeyError:
        return None

    return [ (item['id'], item['name']) for item in j['genres'] ]


def fetch_newreleases(genre):
    start_date = (datetime.datetime.now() + datetime.timedelta(-DAYS_AGO)).strftime("%Y%m%d")
    method = "search/v2/music/filterbrowse"
    args = {
        "entitytype": "album",
        "facet": "genre",
        "filter": "releasedate>%s" % (start_date),
        "filter": "genreid:%s" % (genre[0]),
        "size": "100",
        "offset": "0",
        "country": "US",
        "format": "json"
    }
    print("fetching new releases for %s after %s" % (genre, start_date))
    j = request(method, args)
    try:
        status = j['searchResponse']['controlSet']['status'].strip()
        if status != "ok":
            return None
    except KeyError:
        return None;

    return j['searchResponse']['results']

def parse_albums(name, albums):
    if albums is None:
        # something went wrong
        return

    list =  []
    start_date = (datetime.datetime.now() + datetime.timedelta(-DAYS_AGO))
    for album in albums:
        # enforce max albums limit
        if len(list) >= MAX_ALBUMS:
            break
        album = album['album']
        title = album['title']
        artist = " ".join([ artist['name'] for artist in album['primaryArtists'] ])
        release_date = album['originalReleaseDate']

        # rovi often includes "re-releases" woth older release dates
        # we filter those out here
        try:
            rdate = datetime.datetime.strptime(release_date, "%Y-%m-%d")
            if rdate < start_date:
                continue
        except ValueError:
            # date string probably contained a '?', ignore it
            continue
        except TypeError:
            # sometimes the date field is empty, we ignore those too
            continue

        list.append (
            {'album': title,
             'artist': artist,
             'date': release_date
            })
    list = sorted(list, key=itemgetter('date'))

    chart_id = slugify(name)
    chart = ChartItem()
    chart['name'] = name
    chart['source'] = SOURCE
    chart['type'] = "Album"
    chart['default'] = 1
    chart['date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    chart['id'] = chart_id
    chart['list'] = list

    # metadata is the chart item minus the actual list plus a size
    metadata_keys = filter(lambda k: k != 'list', chart)
    metadata = { key: chart[key] for key in metadata_keys }
    metadata['size'] = len(list)

    metadatas = newrelease_store.get(SOURCE, {})
    metadatas[chart_id] = metadata
    newrelease_store[SOURCE] = metadatas
    newrelease_store[SOURCE+chart_id] = dict(chart)



if __name__ == '__main__':
    for genre in fetch_genres():
        parse_albums("%s" %(genre[1]), fetch_newreleases(genre))

