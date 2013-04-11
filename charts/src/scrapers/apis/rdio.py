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
import oauth2 as oauth
import urllib

class Rdio(Chart):
    source_id = "rdio"
    description = "Hear the music that is most popular on Rdio right now, features todays top albums, tracks and artists."
    have_extra = True 
    baseUrl = "http://api.rdio.com/1/"
    consumerKeys = oauth.Consumer('gk8zmyzj5xztt8aj48csaart', 'yt35kakDyW')
    client = oauth.Client(consumerKeys)
    # Regions, might change http://www.rdio.com/availability/
    regions = [ "US", "SE", "CA", "DE", "GB", "AU",
                "BE", "BR", "DK", "EE", "FI", "FR",
                "IS", "IE","IT", "LV", "LT", "NL",
                "NZ", "NO", "PT", "ES"]
    defaultRegion = "US"
    defaultType = "Track"
    # We are gonna skip playlist here, cuz its crazy, and returns one playlist, like iTunes Top 200 U.S. 11-01-11 for instance. Baaad
    baseTypes = ["Artist", "Album", "Track"]

    def init(self):
        self.setChartName("Top Overall")
        self.setChartDisplayName(self.chart_name)
        self.setExpiresInDays(1)

    def parse(self):
        for baseType in self.baseTypes :
            for region in self.regions :
                if region == self.defaultRegion and baseType == self.defaultType:
                    self.setIsDefault(1)
                self.parseUrl(baseType, region)

    def parseUrl(self, type, region):
        response, contents = self.client.request(self.baseUrl, 'POST', urllib.urlencode({
            'method' : 'getTopCharts',
            'type' : type,
            '_region' : region
        }))

        if( response['status'] !=  '200' ) :
            print "Error " + response['status']
            return

        self.setChartOrigin(self.baseUrl)
        self.setChartType(type)
        self.setChartId(slugify("%s %s %s" % (self.chart_name, type, region)))
        self.setChartGeo(region)

        jsonContent = self.getJsonFromResponse(contents)

        chart_list = []
        for rank, items in enumerate(jsonContent['result']) :
            t = {}
            if( type == "Artist"):
                t["artist"] = items.pop("name")
            else:
                t['artist'] = items.pop("artist")
                t[type.lower()] = items.pop("name")
            t["rank"] = rank 
            chart_list.append(t)
        self.storeChartItem(chart_list)

if __name__ == '__main__':
    Rdio()
