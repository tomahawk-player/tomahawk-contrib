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

    '''
        bcList is a list of backward compatible sources, that means no NEW sources with Geo/Extra/Genre types!
        ONLY
            [Source] - Album - Chart
            [Source] - Track - Chart
    '''
    __bcList = {}

    '''
        sourceList has sources that can be added to Tomahawk versions greater than latest stable
        That means, charts that requires Tomahawk to be updated, to enable Geo/Extra/Genre types!
        ONLY
            [Source] - [GEO]    - [Type] - Chart
                       [EXTRA]  - [Type] - Chart
    '''
    __sourceList = {}

    '''
        Add sources, if no Name is given, a titled id will be used as prettyName.
    '''
    def __init__(self):
        self.update(self.__bcList, id = "itunes", name = "iTunes", desc = "Updated daily, browse what currently hot on Itunes. Includes albums, tracks by genre.")
        self.update(self.__bcList, id = "billboard", desc = "The week's top-selling and most played albums and tracks across all genres, ranked by sales data and radio airtime as compiled by Nielsen.")
        self.update(self.__bcList, id = "soundcloudwall",  desc = "SoundCloudWall publishes a playlist of the 1000 most influential tracks on SoundCloud each month.")
        self.update(self.__bcList, id = "we are hunted", desc = "Publishes awesome music charts, recognised by industry insiders as the best source of new music in the world today.")
        self.update(self.__bcList, id = "rdio",  desc = "Hear the music that is most popular on Rdio right now, features todays top albums, tracks and artists.")
        self.update(self.__bcList, id = "ex.fm", desc = "Discover a pool of great music. Featuring tracks by genres, weekly mix-tapes, mashups and more.")

        self.update(self.__sourceList, id = "djshop.de", name = "djShop.de", desc = "Updated daily with what's currently hot on the electronic scene.")
        self.update(self.__sourceList, id = "hotnewhiphop",  name = "HotNewHipHop", desc = "Real hip-hop fans collaborates to create HotNewHiphops's daily updated charts.")

        # Build!
        self.__sourceList.update(self.__bcList);

    def update(self, dest, id = None, name = None, desc = None ):
        dest.update(self.__detail(id, name, desc))

    def __detail(self, id = None, name = None, desc = None):
        if not name :
            name = self.__titlecase__(id)
        return { id: {
                    'id' : id, 
                    'name' : name, 
                    'description' : desc, 
                    'image' : "%s%s-logo.png" % (self.__baseImageUrl, id )
                }
              }

    def __titlecase__(self, s):
        return re.sub(r"[A-Za-z]+(['.][A-Za-z]+)?",
                   lambda mo: mo.group(0)[0].upper() +
                              mo.group(0)[1:].lower(),
                   s)

    def __sources(self, sources):
        return { source: Source(source) for source in sources.keys() }

    def backwardComp(self, args):
        version = str(args.get('version'))
        if version is None or parse_version(self.__bcVersion) > parse_version(version) :
            return False
        return True

    def getSources(self, request):
        if not self.backwardComp(request.args):
            return self.__sources(self.__bcList)
        return self.__sources(self.__sourceList)

    def getDetail(self, request, id):
        list = {};
        if not self.backwardComp(request.args):
            list = self.__bcList;
        else :
            list = self.__sourceList;

        try:
            return {"details" : list.get(id) };
        except IndexError:
            return {};

    def getDetails(self, request):
        if not self.backwardComp(request.args):
            return self.__bcList;
        return self.__sourceList

    def filterChart(self, args, chart):
        filters = {'geo' : args.get('geo'), 'type' : args.get('type')}
        if filters.get('geo') is None and filters.get('type') is None :
            return chart

        for fkey in filters.keys():
            if filters[fkey] is not None:
                chart = { itemkey: item for itemkey, item in chart.iteritems() if fkey in item and item[fkey] in filters[fkey] }

        return chart

if __name__ == '__main__':
    print ChartDetails().getSources({'version' : '0.6.99'} )