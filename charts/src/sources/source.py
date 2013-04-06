# Copyright (C) 2011 Casey Link <unnamedrambler@gmail.com>
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

from utils import cache

class Source(object):
    def __init__(self, name):
        self.name = name
        self.details = "%sdetails" % name
        self.cacheControl = "%scacheControl" % name
        return

    def get_detailsForSource(self):
        detail = cache.storage.get(self.details, None)
        return detail if detail else cache.newreleases.get(self.details, None)

    def get_name(self):
        return self.name;

    def chart_list(self):
        return cache.storage.get(self.name)

    def get_chart(self, chart_id):
        return cache.storage.get(self.name+chart_id, None)

    def newreleases_list(self):
        return cache.newreleases.get(self.name)

    def get_cacheControlForChart(self):
        return cache.storage.get(self.cacheControl, None)

    def get_cacheControlForRelease(self):
        return cache.newreleases.get(self.cacheControl, None)

    def get_newreleases(self, chart_id):
        return cache.newreleases.get(self.name+chart_id, None)
