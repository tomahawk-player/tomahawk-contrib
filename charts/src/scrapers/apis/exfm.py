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

import urllib2
import json
from scrapers import settings
from sources.utils import cache as chartCache
from scrapers.items import ChartItem, slugify

#@chartCache.methodcache.cache('parseUrls', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parseUrls():
    url = "http://ex.fm/api/v3/"
    for baseType in ["explore", "trending"] :
        if(baseType == "explore"):
            for genre in ["indie", "electronica", "pop", "rock", "hip-hop", "folk", "blues", "metal", "reggae", "classical", "soul", "experimental", "house", "dubstep", "chillwave", "shoegaze", "punk", "country", "synthpop", "mashup"] :
                parse(baseType, url+baseType+"/"+genre, genre)
        else:
            parse(baseType, url+baseType, None)

def parse(type_id, url, extra):
    music_data = []
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')
    jsonContent = json.loads(content)

    chart_list = []
    source = "ex.fm"
    chart_type = "Track"
    chart_name = type_id.title()+" "+ chart_type.title()+"s"
    chart_id = type_id+chart_type.title()
    if( extra != None ) :
        chart_name += " "+extra.title()
        chart_id += extra

    music_data.append( { "type":type_id, "charts": type_id+chart_type } )

    print("Saving %s - %s" %(source, chart_id))

    chart = ChartItem()
    chart['name'] = chart_name
    chart['source'] = source
    chart['type'] = chart_type
    chart['default'] = 1

    expires = chartCache.timedeltaUntilDays(1)
    cacheControl = chartCache.setCacheControl(expires)
    chart['date'] = cacheControl.get("Date-Modified")
    chart['expires'] = cacheControl.get("Date-Expires")
    chart['maxage'] = cacheControl.get("Max-Age")

    chart['id'] = slugify(chart_id)
    if( extra != None ) :
        chart['genre'] = extra.title()
        chart['default'] = 0
    else:
        chart['default'] = 1

    rank = 0
    for items in jsonContent['songs']:
        t = {}
        rank += 1
        try:
            t["artist"] = items.pop("artist").rstrip().strip()
            t["track"] = items.pop("title").rstrip().strip()
            t["rank"] = rank
        except (AttributeError):
            pass
        chart_list.append(t)
    chart['list'] = chart_list

    # metadata is the chart item minus the actual list plus a size
    metadata_keys = filter(lambda k: k != 'list', chart)
    metadata = { key: chart[key] for key in metadata_keys }
    metadata['size'] = len(chart_list)
    metadatas = chartCache.storage.get(source, {})
    metadatas[chart_id] = metadata
    chartCache.storage[source] = metadatas
    chartCache.storage[source+chart['id']] = dict(chart)
    chartCache.storage[source+"cacheControl"] = dict(cacheControl)
if __name__ == '__main__':
    parseUrls()
