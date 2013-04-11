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
from sources.utils import cache as chartCache
from scrapers.items import ChartItem, DetailItem, Detail, slugify

class Chart(object):
    # This is backward compatible, Types must be singular
    __types = {'album' : 'Album','track' : 'Track','artist' : 'Artist'}
    def __init__(self):
        try:
            self.prettyName
        except AttributeError:
            self.prettyName = None

        self.__setStorage()

        self.details = DetailItem(Detail(
            id = self.source_id,
            name = self.prettyName,
            description = self.description,
            have_extra = self.have_extra
            )
        );
        chartCache.shoveDetails(self.details, self.is_chart)
        self.have_extra = self.have_extra

        #Chart specific optional attributes
        self.geo = None
        self.extra = None
        self.genre = None
        self.source_id = self.details.get('id')
        self.cache_id = "%scacheControl" % self.source_id
        self.default = 0

        self.init()
        self.parse()

    def __setStorage(self):
        try:
            if self.is_chart:
                self.storage = chartCache.storage
            else:
                self.storage = chartCache.newreleases
        except AttributeError:
            self.is_chart = True
            self.storage = chartCache.storage

    def __getCacheControl(self):
        self.cacheControl = chartCache.setCacheControl(self.expires)

    def __createChartItem(self):
        try:
            chart = ChartItem(
                id = slugify(self.chart_id),
                name = self.chart_name,
                display_name = self.display_name,
                origin = self.origin,
                type = self.chart_type,
                default = self.default,
                source = self.source_id,
                date = self.cacheControl.get("Date-Modified"),
                expires = self.cacheControl.get("Date-Expires"),
                maxage = self.cacheControl.get("Max-Age"),
                list = self.chart_list
            )
        except AttributeError:
            print "ChartItem is missing required attributes!"
            raise

        if self.have_extra :
            if self.geo is not None:
                chart['geo'] = self.geo
            if self.genre is not None:
                chart['genre'] = self.genre
            if self.extra is not None:
                chart['extra'] = self.extra

        return chart

    def __updateCache(self, metadata, chart):
        data = self.storage.get(self.source_id, {})
        data[self.chart_id] = metadata
        self.storage[self.source_id] = data
        self.storage[self.source_id+self.chart_id] = dict(chart)
        self.storage[self.cache_id] = dict(self.cacheControl)

    def __createMetadata(self, chart):
        # metadata is the chart item minus the actual list plus a size
        metadata_keys = filter(lambda k: k != 'list', chart)
        metadata = { key: chart[key] for key in metadata_keys }
        metadata['size'] = len(self.chart_list)
        return metadata

    def init(self):
        raise NotImplementedError( "Scraper needs to implement this!")

    def parse(self):
        raise NotImplementedError( "Scraper needs to implement this!")

    def setChartId(self, id):
        self.chart_id = id

    def setChartName(self, name):
        self.chart_name = name.title()

    def setChartOrigin(self, origin):
        self.origin = origin

    def setChartDisplayName(self, name):
        self.display_name = name

    def setIsDefault(self, default):
        self.default = default

    def setChartGenre(self, genre):
        self.genre = genre

    def setChartExtra(self, extra):
        self.extra = extra

    def setChartGeo(self, geo):
        self.geo = geo;

    def setChartType(self, type):
        self.chart_type = self.__types.get(type.lower())

    def setExpiresInDays(self, day, hour = 1):
        self.expires = chartCache.timedeltaUntilDays(day, hour)
        self.__getCacheControl()

    def setExpiresOnDay(self, day, hour = 1):
        self.expires = chartCache.timedeltaUntilWeekday(day, hour)
        self.__getCacheControl()

    def getJsonContent(self, url):
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            return json.loads(content)
        except Exception,e:
            print "Error: %s" % e
            return {}

    def getJsonFromResponse(self, response):
        content = response.decode('utf-8')
        return json.loads(content)

    def storeChartItem(self, chart_list):
        print "Saving chart: %s - %s (%s) : %s" % (self.source_id, self.chart_type, slugify(self.chart_id), self.display_name)
        self.chart_list = chart_list;
        chart = self.__createChartItem()
        self.__updateCache(self.__createMetadata(chart), chart)

