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

from time import gmtime, strftime
import urllib2, urllib
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

def parseUrls():
  url = "http://ex.fm/api/v3/"
  for b in ["explore", "trending"]:
    if(b == "explore"):
       for c in ["indie", "electronica", "pop", "rock", "hip-hop", "folk", "blues", "metal", "reggae", "classical", "soul", "experimental", "house", "dubstep", "chillwave", "shoegaze", "punk", "country", "synthpop", "mashup"]:
         parse(b, url+b+"/"+c, c)
    else:
       parse(b, url+b, "")
         
@methodcache.cache('parse', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parse(id, url, genre):
  
   music_data = []
   req = urllib2.Request(url)
   response = urllib2.urlopen(req)
   the_page = response.read()
   content = the_page.decode('utf-8')
   j = json.loads(content)
   
   type = "Track"
   music_data.append( { "type":id, "charts": id+type } )
   source = "ex.fm"
   chart_id = source+id+type+genre
   print("Saving %s - %s" %(source, chart_id))

   list = storage.get(source, {})

   chart_list = []
   chart_name = id.title()+" "+ type.title()+"s "+genre.title()
   chart_type = type
  
   chart = ChartItem()
   chart['name'] = chart_name
   chart['source'] = source
   chart['type'] = chart_type
   chart['default'] = 1
   chart['date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
   chart['id'] = slugify(chart_name)             
  
   x = []
   i = 1
   for items in j['songs']:
     t = {}
     rank = i
     i += 1
     try:
       t["artist"] = items.pop("artist").rstrip().strip()
       t["track"] = items.pop("title").rstrip().strip()
       t["rank"] = rank
     except (AttributeError):
       pass
     x.append(t)
   
   chart['list'] = x
   
   # metadata is the chart item minus the actual list plus a size
   metadata = {}
   metadata['id'] = id+type+genre
   metadata['name'] = chart_name
   metadata['type'] = chart_type
   if( genre != "" ):
     metadata['genre'] = genre.title()
   else:
     metadata['default'] = 1
   metadata['source'] = source
   metadata['size'] = len(j['songs'])
  
   list[chart_id] = metadata
   storage[source] = list
   storage[chart_id] = dict(chart)
     
parseUrls()  

