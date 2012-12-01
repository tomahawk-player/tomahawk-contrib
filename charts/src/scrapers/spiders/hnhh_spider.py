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

from datetime import datetime, timedelta
from urlparse import urlparse
import dateutil.relativedelta as reldate
from scrapy.conf import settings
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy import log
from scrapers.items import ChartItem, SingleUrlAlbumItem, SingleUrlTrackItem, slugify
from collections import deque
from sources.utils import cache as chartCache


class HNHHSpider(CrawlSpider):
    name = "hotnewhiphop.com"
    allowed_domains = ["hotnewhiphop.com"]
    start_urls = [
        # this is the list of all the charts
        "http://www.hotnewhiphop.com/top100/song/mainstream/month/1/",
        "http://www.hotnewhiphop.com/top100/song/mainstream/alltime/1",
        "http://www.hotnewhiphop.com/top100/song/upcoming/month/1",
        "http://www.hotnewhiphop.com/top100/song/upcoming/alltime/1",
        "http://www.hotnewhiphop.com/top100/mixtape/upcoming/month/1",
        "http://www.hotnewhiphop.com/top100/mixtape/upcoming/alltime/1",
        "http://www.hotnewhiphop.com/top100/mixtape/mainstream/month/1",
        "http://www.hotnewhiphop.com/top100/mixtape/mainstream/alltime/1",

    ]
    # Expires next day at 1AM
    def get_maxAge(self) :
        today = datetime.utcnow()
        expires = datetime.replace(today +  timedelta(days=1),hour=1, minute=0, second=0)
        maxage = expires-today
        return maxage.seconds

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        chart_name = hxs.select('//*[@class="mdn800"]/text()').extract()[0].strip()
        try:
            chart_type = hxs.select('//*[@class="tab-right-active"]/text()').extract()[0].strip()
        except IndexError:
            chart_type = hxs.select('//*[@class="tab-left-active"]/text()').extract()[0].strip()

        if "upcoming" in response.url :
            extra = "Upcoming"
        if "mainstream" in response.url :
            extra = "Mainstream"
        if "alltime" in response.url :
            chart_name += " " + extra
            extra = "Alltime"

        id = chart_name + extra + chart_type    
        chart = ChartItem()
        chart['name'] = chart_name + " " + chart_type
        chart['origin'] = response.url
        chart['source'] = 'hotnewhiphop'
        chart['id'] = slugify(id)
        chart['list'] = []
        chart['extra'] = extra
        cacheControl = chartCache.setCacheControl(self.get_maxAge())
        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")
       
        if "mixtape" in response.url :
            if extra == "Upcoming" :
                chart['default'] = 1
            chart['type'] = "Album"
            loader = SingleUrlAlbumItem()
            urlKey = "url"
            url = "http://www.hotnewhiphop.com/ajax/api/getMixtape/"
        elif "song" in response.url :
            chart['type'] = "Track"
            loader = SingleUrlTrackItem()
            # Later on, if we have a hnhh resolver, this url could be used to
            # get a valid mp3 stream.
            url = "hnhh://www.hotnewhiphop.com/ajax/api/getSong/"
            urlKey = "stream_url"
        else :
            log.msg("Error with %s" %(chart['name']))
            return

        chart_list = []
        rank = 0
        for item in hxs.select('//div[@class="newCell newCell2"]'):
            if chart['type'] == "Album" :
                loader = XPathItemLoader(SingleUrlAlbumItem(), selector=item)
            if chart['type'] == "Track" :
                loader = XPathItemLoader(SingleUrlTrackItem(), selector=item)
            loader.add_xpath(chart['type'].lower(), 'div[@class="centerBlock"]/h3/a/text()')
            loader.add_xpath('artist', 'div[@class="centerBlock"]/a/i/text()')
            loader.add_xpath(urlKey, 'div[@class="centerBlock"]/a/@href')
            single = loader.load_item()
            single[urlKey] = url + urlparse(single[urlKey]).path.split(".")[1]
            rank += 1
            single['rank'] = rank
            chart_list.append(dict(single))

        log.msg("Done with %s" %(chart['name']))
        chart['list'] += chart_list
        return chart
