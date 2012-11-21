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

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import shove
import os

try:
    OUTPUT_DIR = os.environ['OUTPUT_DIR']
except KeyError:
    OUTPUT_DIR = '/Users/hugo/cache'

HTTP_CACHE_DIR = OUTPUT_DIR + '/http'
MAX_THREADS=5
TTL=3600


cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': OUTPUT_DIR+'/cache/data',
    'cache.lock_dir': OUTPUT_DIR+'/cache/lock'
}

def setCacheControl(expiresInSeconds):
    today = datetime.datetime.today()
    expires = today + datetime.timedelta(seconds=expiresInSeconds)
    return {
            "Expires" : (expires - datetime.datetime(1970,1,1)).total_seconds(),
            "Max-Age" : expiresInSeconds,
            "Date-Modified" : today.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "Date-Expires" : expires.strftime("%a, %d %b %Y %H:%M:%S +0000")
           }

methodcache = CacheManager(**parse_cache_config_options(cache_opts))

storage = shove.Shove("file://"+OUTPUT_DIR+'/sources', optimize=False)
newreleases = shove.Shove("file://"+OUTPUT_DIR+'/newreleases', optimize=False)
