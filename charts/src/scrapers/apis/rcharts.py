#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ben Evans <ben@bensbit.co.uk>
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

class Rcharts(Chart):
    source_id = "rcharts"
    name = "rCharts"
    prettyName = "rCharts"
    description = "Reddit generated music charts"
    have_extra = False
    baseUrl = "http://rcharts.bensbit.co.uk"
    sections = ["Music", "listentothis", "dubstep", "trance", "treemusic", "IndieFolk"]
    apiKey = "3f578b3d250b47adb24e193ba933a9b80f31d3f9"

    def init(self):
        self.setChartType("Track")
        self.setExpiresInDays(1)

    def parse(self):
        for section in self.sections:
            response = self.getJsonContent('{baseUrl}/r/{section}.json'.format(baseUrl=self.baseUrl, section=section))

            self.setChartOrigin(self.baseUrl)
            self.setChartName(section.capitalize())
            self.setChartDisplayName(self.chart_name)
            self.setChartId(slugify(self.chart_name))

            result_list = []
            for rank, item in enumerate(response[u'tracks']):
                chart_item = {
                        'rank' : rank,
                        'artist' : item['artist'],
                        'track' : item['title']
                        }
                result_list.append(chart_item)

            self.storeChartItem(result_list)

if __name__ == '__main__':
    Rcharts()
