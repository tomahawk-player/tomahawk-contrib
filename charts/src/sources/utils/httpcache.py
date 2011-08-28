# Copyright (C) 2011 Casey Link <unnamedrambler@gmail.com>
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
#
# Parts of this file are not subject to the GPL. See inline comments.

'''
Implements the FileCache interface from the httplib2 package, and
wraps the Shove library to provide thread-safe caching on disk.
'''

import threading

class CacheStorageLock:
    """
    Lock wrapper for cache storage which do not permit multi-threaded access.
    This class is based off cachestoragelock.py from the feedcache package
    and is Copyright 2007 Doug Hellmann.
    See LICENSE.feedcache for licensing information
    """

    def __init__(self, shelf):
        self.lock = threading.Lock()
        self.shelf = shelf
        return

    def __getitem__(self, key):
        with self.lock:
            return self.shelf[key]

    def get(self, key, default=None):
        with self.lock:
            try:
                return self.shelf[key]
            except KeyError:
                return default

    def __setitem__(self, key, value):
        with self.lock:
            self.shelf[key] = value

class HttpCache(object):

    def __init__(self, storage):
        self.storage = CacheStorageLock(storage)

    def get(self, key):
        return self.storage.get(key, None)

    def set(self, key, value):
        self.storage[key] = value

    def delete(self, key):
        del self.storage[key]

