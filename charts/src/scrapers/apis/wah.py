#!/usr/bin/env python2
import urllib2, urllib
import oauth2 as oauth
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import json
import shove
import sys
sys.path.append('../scrapers')
import settings


cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/cache/data',
    'cache.lock_dir': settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/cache/lock'
}

methodcache = CacheManager(**parse_cache_config_options(cache_opts))
storage = shove.Shove('file://'+settings.GLOBAL_SETTINGS['OUTPUT_DIR']+'/sources')

#@methodcache.cache('parse', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
def parse():
   
   #http://wearehunted.com/api/chart/<chart type>/<period>/
   #http://wearehunted.com/api/chart/<chart name>/<chart type>/<period>/
   #http://wearehunted.com/api/chart/by/<user name>/
   base = "http://wearehunted.com/api/chart/"
   emerging = 1 #http://wearehunted.com/api/chart/singles/1/
   mainstream = 30 #http://wearehunted.com/api/chart/singles/30/
   
   charts = [
     "1",
     "30"
   ]
   
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
    "singles",
    "artists"
   ]
   music_data = []
   
   for c in charts:
     if(c == "1"):
	 id = "Emerging"
     if(c == "30"):
         id = "Mainstream"
     for d in types:
       url = base + d +"/"+c+"/?count=100"
       req = urllib2.Request(url)
       response = urllib2.urlopen(req)
       the_page = response.read()
       content = the_page.decode('utf-8')
       j = json.loads(content)
       
       type = d
       if(d == "singles"):
	 type = "tracks"
       
       music_data.append( { "type":id+d, "charts": id+d } )
       source = "wearehunted"
       chart_id = source+id+d
       print("Saving %s - %s" %(source, chart_id))
      
       list = storage.get(source, {})

       # metadata is the chart item minus the actual list plus a size
       metadata = {}
       metadata['id'] = id+d
       metadata['name'] = "Top "+id
       metadata['type'] = type
       metadata['source'] = "wearehunted"
       metadata['size'] = len(j['results'])
       list[chart_id] = metadata
       storage[source] = list
       storage[chart_id] = dict(j)
     
     
       for e in genres:
	 if( e == "remix" and d == "artists"):
	   continue
	 
         url = base + e +"/"+d+"/"+c+"/?count=100"
         req = urllib2.Request(url)
         response = urllib2.urlopen(req)
         the_page = response.read()
         content = the_page.decode('utf-8')
         j = json.loads(content)
       
        
         music_data.append( { "type":id+d+e, "charts": id+d+e } )
         source = "wearehunted"
         chart_id = source+id+d+e
         print("Saving %s - %s" %(source, chart_id))
      
         list = storage.get(source, {})

         # metadata is the chart item minus the actual list plus a size
         metadata = {}
         metadata['id'] = id+d+e
         metadata['name'] = "Top "+id+ " in "+ e.title()
         metadata['type'] = type
         metadata['source'] = "wearehunted"
         metadata['size'] = len(j['results'])
         list[chart_id] = metadata
         storage[source] = list
         storage[chart_id] = dict(j)   
       
       
       
  
parse()

