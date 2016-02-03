#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from sources.source import Source
from pkg_resources import parse_version
import re

class ChartDetails():
    __bcVersion = '0.6.99'
    __baseImageUrl = 'http://hatchet.is/images/'
    # A list of backward compatible sources, that means no NEW sources with Geo/Extra/Genre
    __generic_sources = ['itunes', 'billboard', 'thisismyjam']
    # A list of new sources, that is not compatible with < 0.6.99.
    __generic_non_compatible_sources = ['metacritic', 'hotnewhiphop', 'djshop.de']

    def __init__(self):
        # Build sources
        self.__backward_comp_size = len(self.__generic_sources)
        self.__generic_sources = self.__generic_sources + self.__generic_non_compatible_sources

    def __sources(self, sources):
        return { source: Source(source) for source in sources }

    def __details(self, sources):
        return [ Source(source).get_detailsForSource() for source in sources ]

    def backwardComp(self, args):
        version = str(args.get('version'))
        if version is None or parse_version(self.__bcVersion) > parse_version(version) :
            return False
        return True

    def getSources(self, request):
        if not self.backwardComp(request.args):
            return self.__sources(self.__generic_sources[:self.__backward_comp_size])
        return self.__sources(self.__generic_sources)

    def getDetail(self, request, id):
        if self.backwardComp(request.args):
            return { 'details' : Source(id).get_detailsForSource() }
        return None

    def getDetails(self, request):
        if not self.backwardComp(request.args):
            return self.__details(self.__generic_sources[:6])
        return self.__details(self.__generic_sources)

    def filterChart(self, args, chart):
        # Ensure that we have plural form for Type > 0.6.99
        if self.backwardComp(args):
            for attr, item in chart.iteritems():
                if 'type' in item and not item['type'].endswith("s"):
                    chart[attr]['type'] = "%ss" % chart[attr]['type']

        filters = {'geo' : args.get('geo'), 'type' : args.get('type')}
        if filters.get('geo') is None and filters.get('type') is None :
            return chart

        for fkey in filters.keys():
            if filters[fkey] is not None:
                chart = { itemkey: item for itemkey, item in chart.iteritems() if fkey in item and item[fkey] in filters[fkey] }

        return chart


