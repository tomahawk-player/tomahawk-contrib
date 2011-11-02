#!/usr/bin/env python2
import urllib
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
  consumer = oauth.Consumer('gk8zmyzj5xztt8aj48csaart', 'yt35kakDyW')
  client = oauth.Client(consumer)
  music_data = []
  # We are gonna skip playlist here, cuz its crazy, and returns one playlist, like iTunes Top 200 U.S. 11-01-11 for instance. Baaad
  for c in ["Artist", "Album", "Track"]:
    #Additional key 'extras' = 'tracks', but in tomahawk chart, we actually want artist, albums and tracks seperated! 
    response, contents = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'getTopCharts', 'type': c})) 
    content = contents.decode('utf-8')
    j = json.loads(content)
    id = "top"+c
    music_data.append( { "type":c, "charts": id } )
    
    source = "rdio"
    chart_id = source+id
    print("Saving %s - %s" %(source, chart_id))

    list = storage.get(source, {})

    # metadata is the chart item minus the actual list plus a size
    metadata_keys = filter(lambda k: k != 'result', j.keys())
    metadata = { key: j[key] for key in metadata_keys }
    metadata['id'] = id
    metadata['name'] = "Top Overall"
    metadata['type'] = c
    metadata['source'] = "rdio"
    metadata['size'] = len(j['result'])
    list[chart_id] = metadata
    storage[source] = list
    storage[chart_id] = dict(j)

parse()