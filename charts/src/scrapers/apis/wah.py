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

import urllib2
import json
from scrapers import settings
from scrapers.chart import Chart
from sources.utils import cache as chartCache

class WeAreHunted(Chart):
    source_id = "we are hunted"
    description = "Publishes awesome music charts, recognised by industry insiders as the best source of new music in the world today."
    # https://gist.github.com/bencevans/5024457
    # http://spotifyapp.wearehunted.com/json/all/<chart type>.json
    baseUrl = "http://spotifyapp.wearehunted.com/json/%s/%s.json"
    types = [
        ("all", "mainstream"),
        ("all", "emerging"),
        ("genre", "rock"),
        ("genre", "alternative"),
        ("genre", "pop"),
        ("genre", "electronic"),
        ("genre", "folk"),
        ("genre", "metal"),
        ("genre", "rap-hip-hop")
    ]

    def __init__(self):
        Chart.__init__(self, self.source_id, self.description)
        self.setExpiresInDays(1, 18)
        self.parse()

    @chartCache.methodcache.cache('parse', expire=settings.GLOBAL_SETTINGS['EXPIRE'])
    def parse(self):
        for modifier, charttype in self.types:
            url = self.baseUrl % (modifier, charttype)

            self.setChartName(charttype)
            self.setChartType("Track")
            self.setChartDisplayName(charttype.title())
            self.setChartId("wah_%s" % charttype);
            self.setIsDefault(1 if "Mainstream" in charttype else 0)
            self.setChartOrigin(url)
            chart_list = []
            json_content = self.getJsonContent(url)

            rank = 0
            for track in json_content['results']:
                trackMap = {}
                rank += 1
                try:
                    trackMap["artist"] = track["artist"].strip()
                    trackMap["track"] = track["track"].strip()
                    trackMap["rank"] = rank
                except (AttributeError):
                    pass
                chart_list.append(trackMap)

            # Stores this chart
            self.storeChartItem(chart_list)

if __name__ == '__main__':
    WeAreHunted()
