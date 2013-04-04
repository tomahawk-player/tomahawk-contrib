#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011-2012 Hugo Lindström <hugolm84@gmail.com>
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
#
# !!NOTE: PYTHONPATH to this project basedir need to be set,
#       Eg. export PYTHONPATH=/path/to/src/

import urllib
import oauth2 as oauth
import json
from scrapers import settings
from sources.utils import cache as chartCache
from scrapers.items import ChartItem, slugify

#@chartCache.methodcache.cache('parseUrls', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parseUrls():

    url = "http://api.rdio.com/1/"
    consumerKeys = oauth.Consumer('gk8zmyzj5xztt8aj48csaart', 'yt35kakDyW')
    client = oauth.Client(consumerKeys)
    # Regions, might change http://www.rdio.com/availability/
    regions = [ "US", "SE", "CA", "DE", "GB", "AU",
                "BE", "BR", "DK", "EE", "FI", "FR",
                "IS", "IE","IT", "LV", "LT", "NL",
                "NZ", "NO", "PT", "ES"]

    # We are gonna skip playlist here, cuz its crazy, and returns one playlist, like iTunes Top 200 U.S. 11-01-11 for instance. Baaad
    for baseType in ["Artist", "Album", "Track"] :
        for region in regions :
            parse(client, url, baseType, region)

def parse(client, url, baseType, region):
    #Additional key 'extras' = 'tracks', but in tomahawk chart, we actually want artist, albums and tracks seperated! 
    response, contents = client.request(url, 'POST', urllib.urlencode({
        'method' : 'getTopCharts',
        'type' : baseType,
        '_region' : region
        }))

    if( response['status'] !=  '200' ) :
        print "Error " + response['status']
    else :
        content = contents.decode('utf-8')
        jsonContent = json.loads(content)

        # TODO: Playlist charts
        if( baseType == "Playlist"):
            print "Playlist not implemented"
        else :
            type_id = "top"+baseType+region
            source = "rdio"
            chart_id = source+type_id
            print("Saving %s - %s (%s)" %(source, chart_id, region))

            cached_list = chartCache.storage.get(source, {})
            chart_list = []
            chart_name = "Top Overall"
            chart_type = baseType.title()

            chart = ChartItem()
            chart['name'] = chart_name
            chart['display_name'] = chart_name
            chart['source'] = source
            chart['type'] = chart_type
            chart['geo'] = region
            chart['id'] = slugify(type_id)
            expires = chartCache.timedeltaUntilDays(1)
            cacheControl = chartCache.setCacheControl(expires)
            chart['date'] = cacheControl.get("Date-Modified")
            chart['expires'] = cacheControl.get("Date-Expires")
            chart['maxage'] = cacheControl.get("Max-Age")

            rank = 0
            for items in jsonContent['result'] :
                t = {}
                rank += 1
                if( baseType == "Artist"):
                    t["artist"] = items.pop("name")
                else:
                    t['artist'] = items.pop("artist")
                    t[baseType.lower()] = items.pop("name")
                t["rank"] = rank 
                chart_list.append(t)

            chart['list'] = chart_list

            # metadata is the chart item minus the actual list plus a size
            metadata_keys = filter(lambda k: k != 'result', jsonContent.keys())
            metadata = { key: jsonContent[key] for key in metadata_keys }
            metadata['id'] = type_id
            metadata['name'] = chart_name
            metadata['display_name'] = chart_name
            metadata['geo'] = region
            metadata['type'] = baseType
            metadata['source'] = source
            metadata['date'] = cacheControl.get("Date-Modified")
            metadata['expires'] = cacheControl.get("Date-Expires")
            metadata['maxage'] = cacheControl.get("Max-Age")

            if( baseType == "Track") :
                metadata['default'] = 1

            metadata['size'] = len(jsonContent['result'])
            cached_list[chart_id] = metadata
            chartCache.storage[source] = cached_list
            chartCache.storage[chart_id] = dict(chart)
            chartCache.storage[source+"cacheControl"] = dict(cacheControl)

if __name__ == '__main__':
    parseUrls()
