#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Hugo Lindström <hugolm84@gmail.com>
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

from time import gmtime, strftime
import datetime
import urllib2, urllib
import calendar
import oauth2 as oauth
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
storage = shove.Shove('file://'+settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/sources')

def createUrl():
   #http://www.soundcloudwall.com/api/chart/<year>/<month>
   #http://www.soundcloudwall.com/api/chart/2011/october
   base = "http://www.soundcloudwall.com/api/chart/"
   now = datetime.datetime.now()
   default = 0
   for y in range(2011, now.year+1):
      maxrange = now.month
      minrange = 1
      if( y == 2011 ):
	     maxrange = 12
	     minrange = 5
      
      url = base + str(y)
      basetitle = "1000 Most Influential Tracks of "
      title = basetitle + str(y)
      parseUrl(url, title, default)
      for i in range(minrange,maxrange+1):
	     if( now.year == y and now.month == i):
		    default = 1
	     title = basetitle + calendar.month_name[i] + " " + str(y)
	     parseUrl( url + "/" + calendar.month_name[i], title, default )

# We would like to store the cache forever, solution? For now, expire in one year	
@methodcache.cache('parseUrl', expire=31556926 )     
def parseUrl(url, title, default):
	music_data = []
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	the_page = response.read()
	content = the_page.decode('utf-8')
	j = json.loads(content)
	
	type = "Track"
	id = slugify(title)
	source = "soundcloudwall.com"
	chart_id = source+id
	
	print("Saving %s - %s" %(source, chart_id))

	list = storage.get(source, {})

	chart_list = []
	chart_name = title.title()
	chart_type = type
	chart = ChartItem()
	chart['name'] = chart_name
	chart['source'] = source
	chart['type'] = chart_type
	chart['default'] = default
	chart['date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
	chart['id'] = slugify(chart_name)           

	x = []
	i = 1
	for items in j:
	   t = {}
	   rank = i
	   i += 1
	   try:
	     t["artist"] = items.pop("username").rstrip().strip()
	     t["track"] = items.pop("title").rstrip().strip()
	     t["rank"] = rank
	     t['stream_url'] = "http://api.soundcloud.com/tracks/" + str(items.pop("id")) + "/stream.json?client_id=TiNg2DRYhBnp01DA3zNag" 
	   except (AttributeError):
	     pass
	   x.append(t)

	chart['list'] = x
	# metadata is the chart item minus the actual list plus a size
	metadata = {}
	metadata['id'] = id
	metadata['name'] = chart_name
	metadata['type'] = chart_type
	metadata['default'] = default
	metadata['source'] = source
	metadata['size'] = len(j)

	list[chart_id] = metadata
	storage[source] = list
	storage[chart_id] = dict(chart)
	
createUrl()