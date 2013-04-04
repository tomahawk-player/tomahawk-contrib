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
from datetime import datetime, timedelta
from scrapers import settings
from sources.utils import cache as chartCache
from scrapers.items import ChartItem, slugify


def secondsTillTomorrow():
    today = datetime.utcnow()
    expires = datetime.replace(today +  timedelta(days=1),hour=1, minute=0, second=0)
    maxage = expires-today
    return maxage.seconds

@chartCache.methodcache.cache('parse', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parse():

    # https://gist.github.com/bencevans/5024457
    # http://spotifyapp.wearehunted.com/json/all/<chart type>.json
    base = "http://spotifyapp.wearehunted.com/json/%s/%s.json"

    types = [
    ("all", "mainstream"),
    ("all", "emerging"),
    ("genre", "rock"),
    ("genre", "alternative"),
    ("genre", "pop"),
    ("genre", "electronic"),
    ("genre", "folk"),
    ("genre", "metal"),
    ("genre", "rap-hip-hop")
    ]

    for modifier, charttype in types:
        url = base % (modifier, charttype)

        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        content = response.read().decode('utf-8')
        json_content = json.loads(content)


        chart_list = []
        source = "we are hunted"
        content_type = "Track"
        chart_name = source + " " + charttype
        chart_id = "wah_" + charttype

        print "Saving chart: %s - %s (%s)" % (source, charttype, slugify(chart_id))

        chart = ChartItem()
        chart['name'] = charttype.title()
        chart['display_name'] = chart["name"] if chart["name"] else "Top Overall"
        chart['source'] = source
        chart['type'] = content_type
        chart['default'] = 1 if "Mainstream" in chart["name"] else 0

        # Seems to be updated each day at 6
        expires = chartCache.timedeltaUntilDays(1, 18)
        cacheControl = chartCache.setCacheControl(expires)

        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")

        chart['id'] = slugify(chart_id)

        chart_list = []
        rank = 0
        for track in json_content['results']:
            trackMap = {}
            rank += 1
            try:
                trackMap["artist"] = track["artist"].strip()
                trackMap["track"] = track["track"].strip()
                trackMap["rank"] = rank
            except (AttributeError):
                pass
            chart_list.append(trackMap)

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
    parse()
