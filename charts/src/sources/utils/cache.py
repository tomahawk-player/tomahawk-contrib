#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Casey Link <unnamedrambler@gmail.com>
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

"""
Contains information regarding caching behavior
"""


from datetime import datetime, timedelta
import dateutil.relativedelta as reldate
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import shove
import os

try:
    OUTPUT_DIR = os.environ['OUTPUT_DIR']
except KeyError:
    OUTPUT_DIR = os.path.join(os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')), 'cache')

HTTP_CACHE_DIR = os.path.join(OUTPUT_DIR, 'http')
MAX_THREADS=5
TTL=3600


cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': os.path.join(OUTPUT_DIR, 'cache', 'data'),
    'cache.lock_dir': os.path.join(OUTPUT_DIR, 'cache', 'lock'),
}

methodcache = CacheManager(**parse_cache_config_options(cache_opts))
storage = shove.Shove("file://"+OUTPUT_DIR+'/sources', optimize=False)
newreleases = shove.Shove("file://"+OUTPUT_DIR+'/newreleases', optimize=False)

# Note: Weekday starts on 0. eg. 3 = Thursday
def timedeltaUntilWeekday(weekday, hour) :
    today = datetime.utcnow()
    expires = today+reldate.relativedelta(minute=0,hour=hour,weekday=weekday)
    return {'expires' : expires-today, 'date' : expires, 'seconds' :  (expires-today).total_seconds() }

# Default expires next day at 1AM
def timedeltaUntilDays(days=1, hour=1) :
    today = datetime.utcnow()
    expires = datetime.replace(today + timedelta(days=days), hour=hour, minute=0, second=0)
    return dict({"expires" : expires-today, "date" : expires, 'seconds' :  (expires-today).total_seconds() })

def setCacheControl(delta):
    today = datetime.utcnow()
    expires = today + timedelta(seconds=delta['seconds'])
    return {
        "Expires" : int((expires - datetime.utcfromtimestamp(0)).total_seconds()),
        "Max-Age" : int(delta['seconds']),
        "Date-Modified" : today.strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "Date-Expires" : expires.strftime("%a, %d %b %Y %H:%M:%S +0000")
    }

def shoveDetails(details, isChart = True):
    if isChart:
        storage["%s%s" % (details.get('id'), "details")] = dict(details)
    else:
        newreleases["%s%s" % (details.get('id'), "details")] = dict(details)

def appendCacheHeader(source, response, isChart = True):
    if isChart:
        cacheControl = source.get_cacheControlForChart()
    else:
        cacheControl = source.get_cacheControlForRelease();
    try:
        for key in cacheControl.keys() :
            response.headers.add(key, cacheControl[key])
    except Exception, e:
        print "Cache Error: %s" % e
    return response;

def appendExpireHeaders(request, sources, response, isChart = True):
    for source in sources:
        source = sources.get(source, None)
        try:
            if isChart:
                expires = source.get_cacheControlForChart()['Expires'];
            else:
                expires = source.get_cacheControlForRelease()['Expires']
            response.headers.add(source.get_name() + 'Expires', expires)
        except Exception, e:
            print "Expiration Error: %s" % e
    return response

