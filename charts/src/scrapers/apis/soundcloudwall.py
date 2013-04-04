#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Hugo Lindström <hugolm84@gmail.com>
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
import urllib2
import calendar
import json
from scrapers.items import ChartItem, slugify
from sources.utils import cache as chartCache

EXPIRES = 365 #One year
API_KEY = "TiNg2DRYhBnp01DA3zNag"
BASE_TITLE = "100 Most Influential Tracks of "

def createUrl():
    #http://www.soundcloudwall.com/api/chart/<year>/<month>
    #http://www.soundcloudwall.com/api/chart/2011/october
    base = "http://www.soundcloudwall.com/api/chart/"
    now = datetime.datetime.now()
    default = 0
    for year in range(2011, now.year+1):
        maxrange = now.month
        minrange = 1
        if( year == 2011 ):
            maxrange = 12
            minrange = 5

        url = base + str(year)
        
        title = BASE_TITLE + str(year)
        parseUrl(url, title, default)
        for month in range(minrange,maxrange+1):
            if( now.year == year and now.month == month):
                default = 1
            title = BASE_TITLE + calendar.month_name[month] + " " + str(year)
            parseUrl( url + "/" + calendar.month_name[month], title, default )

# We would like to store the cache forever, solution? For now, expire in one year
@chartCache.methodcache.cache('parseUrl', expire=EXPIRES)
def parseUrl(url, title, default):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    content = the_page.decode('utf-8')
    jsonContent = json.loads(content)

    if( len(jsonContent) != 0 ):

        _type = "Track"
        _id = slugify(title)
        source = "soundcloudwall"
        chart_id = source+_id

        print("Saving %s - %s" %(source, chart_id))

        chart_list = []
        chart_name = title.title()
        chart_type = _type
        chart = ChartItem()
        chart['name'] = chart_name
        chart['display_name'] = chart_name if chart_name else "Top Overall"
        chart['source'] = source
        chart['type'] = chart_type
        chart['default'] = default
        expires = chartCache.timedeltaUntilDays(EXPIRES)
        cacheControl = chartCache.setCacheControl(expires)
        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")

        rank = 0
        count = 0;
        for items in jsonContent:
            item = {}
            rank += 1
            # We only take the first 100
            if( count < 100):
                # Soundcloud metadata is hard
                try:
                    item["track"] = items.pop("title").rstrip().strip()
                    try:
                        item["artist"] = item["track"][:item["track"].index(" - ")]
                        item["track"] = item["track"][item["track"].index(" - ")+3:]
                    except (ValueError):
                        try:
                            item["artist"] = item["track"][:item["track"].index(" -")]
                            item["track"] = item["track"][item["track"].index(" -")+2:]
                        except (ValueError):
                            try:
                                item["artist"] = item["track"][:item["track"].index(": ")]
                                item["track"] = item["track"][item["track"].index(": ")+2:]
                            except (ValueError):
                                try:
                                    item["artist"] = item["track"][:item["track"].index(":")]
                                    item["track"] = item["track"][item["track"].index(":")+1:]
                                except (ValueError):
                                    try:
                                        item["artist"] = item["track"][:item["track"].index("\u2014")]
                                        item["track"] = item["track"][item["track"].index("\u2014")+1:]
                                    except (ValueError):
                                        item["artist"] = items.pop("username").rstrip().strip()
                                        
                    item["rank"] = rank
                    item['stream_url'] = "http://api.soundcloud.com/tracks/" + str(items.pop("id")) + "/stream.json?client_id=%s" % (API_KEY)
                except (AttributeError):
                    pass
                count += 1
                chart_list.append(item)

            chart['list'] = chart_list
            metadata_keys = filter(lambda k: k != 'list', chart)
            metadata = { key: chart[key] for key in metadata_keys }
            metadata['size'] = len(chart_list)
            metadatas = chartCache.storage.get(source, {})
            metadatas[chart_id] = metadata
            chartCache.storage[source] = metadatas
            chartCache.storage[chart_id] = dict(chart)
            chartCache.storage[source+"cacheControl"] = dict(cacheControl)

if __name__ == '__main__':
    createUrl()