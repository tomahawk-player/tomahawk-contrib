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


from scrapers import settings
from scrapers.chart import Chart
from sources.utils import cache as chartCache
from scrapers.items import slugify

class Exfm(Chart):
    source_id = "ex.fm"
    description = "Discover a pool of great music. Featuring tracks by genres, weekly mix-tapes, mashups and more."
    have_extra = False
    baseUrl = "http://ex.fm/api/v3/"
    genres = ["indie", "electronica", "pop", "rock", "hip-hop", "folk", "blues", "metal",
             "reggae", "classical", "soul", "experimental", "house", "dubstep", "chillwave",
             "shoegaze", "punk", "country", "synthpop", "mashup"
    ]

    def init(self):
        self.setChartType("Track")
        self.setExpiresInDays(1)

    def parse(self):
        self.exfmType = "explore"
        for genre in self.genres:
            self.url = "%s%s/%s" % (self.baseUrl, self.exfmType, genre)
            self.parseUrl(self.url, genre)

        self.exfmType = "trending"
        self.setIsDefault(1)
        self.url = "%s%s" % (self.baseUrl, self.exfmType)
        self.parseUrl(self.url) 

    def parseUrl(self, url, extra = None):
        self.setChartName("%s %ss" % (self.exfmType.title(), self.chart_type.title()))
        self.setChartDisplayName(extra.title() if extra else self.exfmType.title())
        self.setChartOrigin(url)

        if extra:
            self.setChartName("%s %s" % (self.chart_name, extra))
        self.setChartId(slugify(self.chart_name))

        jsonContent = self.getJsonContent(url)

        chart_list = []
        for rank, items in enumerate(jsonContent['songs']):
            t = {}
            try:
                t["artist"] = items.pop("artist").rstrip().strip()
                t["track"] = items.pop("title").rstrip().strip()
                t["rank"] = rank
            except (AttributeError):
                pass
            chart_list.append(t)
        self.storeChartItem(chart_list)

if __name__ == '__main__':
    Exfm()
