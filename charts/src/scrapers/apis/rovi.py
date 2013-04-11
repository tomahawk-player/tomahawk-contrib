#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Casey Link <unnamedrambler@gmail.com>
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

from time import time
import datetime
from operator import itemgetter
import urllib, urllib2
import md5
from scrapers.chart import Chart
from sources.utils import cache as chartCache
from scrapers.items import slugify
import re

class Rovi(Chart):
    source_id = "rovi"
    description = "Enjoy the latest music gathered by Rovi Corp."
    have_extra = True
    is_chart = False
    baseUrl = "http://api.rovicorp.com/"
    apiKey = "7jxr9zggt45h6rg2n4ss3mrj"
    apiSecret = "XUnYutaAW6"
    daysAgo = 365
    maxAlbums = 100
    baseArgs = {
        "entitytype": "album",
        "facet": "genre",
        "size": "1000",
        "offset": "0",
        "country": "US",
        "format": "json"
    }
    def init(self):
        self.setExpiresInDays(1)

    def parse(self):
        for genre in self.fetch_genres():
            self.parse_albums("%s" %(genre[1]), self.fetch_newreleases(genre), False)
            self.parse_albums("%s" %(genre[1]), self.fetch_neweditorials(genre), True)

    def __make_sig(self):
        pre_sig = self.apiKey+self.apiSecret+str(int(time()))
        m = md5.new()
        m.update(pre_sig)
        return m.hexdigest()

    def __sign_args(self, args):
        args['apikey'] = self.apiKey
        args['sig'] = self.__make_sig()
        return args

    def __request(self, method, args, additionalValue=None):
        args = self.__sign_args(args);
        url = "%s%s?%s%s" % (self.baseUrl, method, urllib.urlencode(args), additionalValue if additionalValue is not None else "" )
        self.setChartOrigin(url)
        print("fetching: " + url)
        return self.getJsonContent(url)

    @chartCache.methodcache.cache('fetch_genres', expire=86400)
    def fetch_genres(self):
        method = "data/v1/descriptor/musicgenres"
        args = {
            "country": "US",
            "format": "json",
            "language": "en"
        }
        j = self.__request(method, args)
        try:
            if j['status'].strip() != "ok":
                return None
        except KeyError:
            return None

        return [ (item['id'], item['name']) for item in j['genres'] ]

    def fetch_neweditorials(self, genre):
        method = "search/v2/music/filterbrowse"
        args = self.baseArgs
        args["filter"] = "genreid:%s" % (genre[0])
        print("fetching new editorials for %s within %s" % (genre, datetime.datetime.now().year-1))
        j = self.__request(method, args,"&filter=releaseyear>:%s%s" % (datetime.datetime.now().year-1, "&filter=editorialrating>:7"))
        try:
            status = j['searchResponse']['controlSet']['status'].strip()
            if status != "ok":
                return None
        except KeyError:
            return None;

        return j['searchResponse']['results']

    def fetch_newreleases(self, genre):
        method = "search/v2/music/filterbrowse"
        args = self.baseArgs
        args["filter"] = "genreid:%s" % (genre[0])
        print("fetching new releases for %s within %s" % (genre, datetime.datetime.now().year-1))
        j = self.__request(method, args,"&filter=releaseyear>:%s" % (datetime.datetime.now().year-1))
        try:
            status = j['searchResponse']['controlSet']['status'].strip()
            if status != "ok":
                return None
        except KeyError:
            return None;

        return j['searchResponse']['results']

    def parse_albums(self, name, albums, isEditorial ):
        if albums is None:
            # something went wrong
            return

        self.setChartName(name)
        self.setChartDisplayName(name)
        self.setChartType("Album")
        self.setChartId(slugify("%s%s" % (self.source_id, name) if isEditorial is True else "%seditorial %s" % (self.source_id,name)))
        self.setChartExtra("Editorial Choices") if isEditorial else self.setChartExtra(None)

        chart_list =  []
        nullList = []
        for album in albums:
            try:
                album = album['album']
                title = album['title']
                artist = " ".join([ artist['name'] for artist in album['primaryArtists'] ])
                try:
                    review = album['headlineReview']
                    try:
                        review['text'] = re.sub(r'((\[roviLink=.+])(.*?)(\[/roviLink]))', r'\3', review['text'])
                    except Exception,e:
                        print e
                except Exception:
                    review = None

                release_date = album['originalReleaseDate']
                rating = album['rating']
                # instead of filter out by releasedate, we search the api by releaseyear
                # the result seems to be more appealing
                # Note: some albums have Null releaseDate, this doesnt necessarily mean
                # that the release date isnt within our range. We include some of them as well
                if release_date is not None :
                    chart_list.append (
                        {'album': title,
                         'artist': artist,
                         'date': release_date,
                         'rating': rating,
                         'review' : review
                     })
                else :
                    nullList.append (
                       {'album': title,
                        'artist': artist,
                        'date': release_date,
                        'rating': rating,
                         'review' : review
                    })
            except :
                continue

        if(len(nullList) > self.maxAlbums):
            print("Slicing NUllList from %s to %s" %(len(nullList), self.maxAlbums))
            nullList = nullList[-self.maxAlbums:]

        chart_list = sorted(chart_list, key=itemgetter('date'))
        if(len(chart_list) > self.maxAlbums):
            print("Slicing list from %s to %s" %(len(chart_list), self.maxAlbums))
            chart_list = chart_list[-self.maxAlbums:]

        _list = nullList + chart_list
        self.storeChartItem(_list)

if __name__ == '__main__':
    Rovi()
