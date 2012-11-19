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

import datetime
import urllib2
import json
from scrapers import settings
from sources.utils import cache as chartCache
from scrapers.items import ChartItem, slugify

@chartCache.methodcache.cache('parse', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parse():
    
    #http://wearehunted.com/api/chart/<chart type>/<period>/
    #http://wearehunted.com/api/chart/<chart name>/<chart type>/<period>/
    #http://wearehunted.com/api/chart/by/<user name>/
    base = "http://wearehunted.com/api/chart/"

    charts = [ "1","30"]

    genres = [
    "rock",
    "pop",
    "folk",
    "metal",
    "alternative",
    "electronic",
    "punk",
    "rap-hip-hop",
    "twitter",
    "remix"
    ]
    
    types = [
    "singles"
    ]
    music_data = []
    
    today = datetime.datetime.today()
    expires = today + datetime.timedelta(seconds=settings.GLOBAL_SETTINGS['EXPIRE'])
    for _id in charts:
        if(_id == "1"):
            type_id = "Emerging"
        if(_id == "30"):
            type_id = "Mainstream"
        for _type in types:
            url = base + _type +"/"+_id+"/?count=100"
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            the_page = response.read()
            content = the_page.decode('utf-8')
            j = json.loads(content)
            if(_type == "singles"):
                _type = "tracks"

            music_data.append( { "type":type_id+_type, "charts": type_id+_type } )
            source = "wearehunted"
            chart_id = source+type_id+_type
            print("Saving %s - %s" %(source, chart_id))
            
            cached_list = chartCache.storage.get(source, {})

            #chart_list = []
            chart_name = "Top "+type_id
            chart_type = _type[:-1].title()

            chart = ChartItem()
            chart['name'] = chart_name
            chart['source'] = "wearehunted"
            chart['type'] = chart_type
            chart['default'] = 1
            chart['id'] = slugify(chart_name)
            chart['list'] = j['results']
            chart['date'] = today.strftime("%a, %d %b %Y %H:%M:%S +0000")
            chart['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S +0000")
            chart['maxage'] = settings.GLOBAL_SETTINGS['EXPIRE']
            # metadata is the chart item minus the actual list plus a size
            metadata = {}
            metadata['id'] = type_id+_type
            metadata['name'] = chart_name
            metadata['type'] = chart_type
            metadata['extra'] = type_id
            if( _id == "1"):
                metadata['default'] = 1
            metadata['source'] = "wearehunted"
            metadata['size'] = len(j['results'])
            metadata['maxage'] = chart['maxage']
            metadata['date'] = chart['date']
            metadata['expires'] = chart['expires']
            cached_list[chart_id] = metadata
            chartCache.storage[source] = cached_list
            chartCache.storage[chart_id] = dict(chart)

            for genre in genres:
                if( genre == "remix" and _type == "artists"):
                    continue

                url = base + genre +"/"+_type+"/"+_id+"/?count=100"
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                the_page = response.read()
                content = the_page.decode('utf-8')
                j = json.loads(content)


                music_data.append( { "type":_id+_type+genre, "charts": _id+_type+genre } )
                chart_id = source+_id+_type+genre
                print("Saving %s - %s" %(source, chart_id))

                cached_list = chartCache.storage.get(source, {})

                #chart_list = []
                chart_name = "Top "+type_id+ " in "+ genre.title()
                chart_type = _type[:-1].title()

                chart = ChartItem()
                chart['name'] = chart_name
                chart['source'] = "wearehunted"
                chart['type'] = chart_type
                chart['id'] = slugify(chart_name)
                chart['list'] = j['results']
                chart['date'] = today.strftime("%a, %d %b %Y %H:%M:%S +0000")
                chart['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S +0000")
                chart['maxage'] = settings.GLOBAL_SETTINGS['EXPIRE']

                # metadata is the chart item minus the actual list plus a size
                metadata = {}
                metadata['id'] = type_id+_type+genre
                metadata['name'] = chart_name
                metadata['type'] = chart_type
                metadata['genre'] = genre.title()
                metadata['extra'] = type_id
                metadata['maxage'] = chart['maxage']
                metadata['date'] = chart['date']
                metadata['expires'] = chart['expires']
                metadata['source'] = "wearehunted"
                metadata['size'] = len(j['results'])
                cached_list[chart_id] = metadata
                chartCache.storage[source] = cached_list
                chartCache.storage[chart_id] = dict(chart)

if __name__ == '__main__':
    parse()
