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


import datetime
import urllib2
import calendar
import json
from scrapers import settings
from scrapers.chart import Chart
from sources.utils import cache as chartCache
from scrapers.items import slugify

class Soundcloudwall(Chart):
    source_id = "soundcloudwall"
    description = "SoundCloudWall publishes a playlist of the 1000 most influential tracks on SoundCloud each month."
    have_extra = False
    #http://www.soundcloudwall.com/api/chart/<year>/<month>
    #http://www.soundcloudwall.com/api/chart/2011/october
    baseUrl = "http://www.soundcloudwall.com/api/chart/"
    baseTitle = "100 Most Influential Tracks of"
    apiKey = "TiNg2DRYhBnp01DA3zNag"

    def init(self):
        self.setExpiresInDays(365)

    def parse(self):
        default = 0
        self.setChartType("Track")
        for year in range(2011, 2012+1):
            max_monthrange = 12 if year is 2011 else 11
            min_monthrange = 5 if year is 2011 else 1

            self.setChartName("%s %s" % (self.baseTitle, year))
            self.setIsDefault(default)
            self.url = "%s%s" % (self.baseUrl, year)
            self.parseUrl()

            for month in range(min_monthrange,max_monthrange+1):
                if( year == 2012 and month == max_monthrange):
                    default = 1
                self.setChartName("%s %s %s" % (self.baseTitle, calendar.month_name[month], year))
                self.setIsDefault(default)
                self.url = "%s%s/%s" % (self.baseUrl, year, calendar.month_name[month])
                self.parseUrl()

    def parseUrl(self):
        print "%s %s" % (self.chart_name, self.url)
        self.setChartId(slugify(self.chart_name))
        self.setChartDisplayName(self.chart_name)
        self.setChartOrigin(self.url)

        chart_list = []

        jsonContent = self.getJsonContent(self.url)

        if( len(jsonContent) != 0 ):
            rank = 0
            count = 0;
            for rank, items in enumerate(jsonContent):
                item = {}
                # We only take the first 100
                if( count < 100):
                    # Soundcloud metadata is hard
                    try:
                        item["track"] = items.pop("title").rstrip().strip()
                        try:
                            item["artist"] = item["track"][:item["track"].index(" - ")]
                            item["track"] = item["track"][item["track"].index(" - ")+3:]
                        except (ValueError):
                            try:
                                item["artist"] = item["track"][:item["track"].index(" -")]
                                item["track"] = item["track"][item["track"].index(" -")+2:]
                            except (ValueError):
                                try:
                                    item["artist"] = item["track"][:item["track"].index(": ")]
                                    item["track"] = item["track"][item["track"].index(": ")+2:]
                                except (ValueError):
                                    try:
                                        item["artist"] = item["track"][:item["track"].index(":")]
                                        item["track"] = item["track"][item["track"].index(":")+1:]
                                    except (ValueError):
                                        try:
                                            item["artist"] = item["track"][:item["track"].index("\u2014")]
                                            item["track"] = item["track"][item["track"].index("\u2014")+1:]
                                        except (ValueError):
                                            item["artist"] = items.pop("username").rstrip().strip()
                                            
                        item["rank"] = rank
                        item['stream_url'] = "http://api.soundcloud.com/tracks/" + str(items.pop("id")) + "/stream.json?client_id=%s" % (self.apiKey)
                    except (AttributeError):
                        pass
                    count += 1
                    chart_list.append(item)
        # Stores this chart
        self.storeChartItem(chart_list)

if __name__ == '__main__':
    Soundcloudwall()