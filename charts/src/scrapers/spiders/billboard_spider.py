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

from datetime import datetime, timedelta
import dateutil.relativedelta as reldate
from scrapy.conf import settings
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy import log
from scrapers.items import ChartItem, SingleTrackItem, SingleAlbumItem, SingleArtistItem, slugify
from collections import deque
from sources.utils import cache as chartCache

EXPIRES_DAY = 3 #Thursday
EXPIRES_HOUR = 13 # After noon, 12pm Pacific 

class BillboardSpider(CrawlSpider):
    name = "billboard.com"
    allowed_domains = ["billboard.com"]
    start_urls = [
        # this is the list of all the charts
        "http://www.billboard.com/charts"
    ]

    # xpath to retrieve the urls to specific charts
    chart_xpath = '//span[@class="field-content"]/a'
    # the xpath to the pagination links
    next_page_xpath = '//div[@class="chart_pager_bottom"]/div/ul/li[@class="pager-item"]/a/@href'
    # we only need one rule, and that is to follow
    # the links from the charts list page
    rules = [
        Rule(SgmlLinkExtractor(allow=['/charts/\w+'], restrict_xpaths=chart_xpath), callback='parse_chart', follow=True)
    ]

    def get_maxAge(self) :
        today = datetime.utcnow()
        expires = today+reldate.relativedelta(minute=0,hour=EXPIRES_HOUR,weekday=EXPIRES_DAY)
        maxage = expires-today
        return maxage.total_seconds()

    def parse_chart(self, response):
        hxs = HtmlXPathSelector(response)

        chart_name = hxs.select('//h1[@id="page-title"]/text()').extract()[0].strip()
        #chart_type = hxs.select('//*[@id="chart-list"]/div[@id="chart-type-fb"]/text()').extract()[0].strip()

        # get a list of pages
        next_pages = hxs.select(self.next_page_xpath).extract()
        # remove javascript links and turn it into a queue, also, we want to exclude next chart (!)
        next_pages = deque(filter(lambda e: not 'javascript' in e, next_pages))

        # Correct the grammar to fit our expectations
        if chart_name == 'Germany Songs':
            chart_name = 'German Tracks'
        
        chart = ChartItem()
        chart['name'] = chart_name
        chart['origin'] = response.url
        chart['source'] = 'billboard'
        chart['id'] = slugify(chart_name)
        chart['list'] = []
    
        cacheControl = chartCache.setCacheControl(self.get_maxAge())
        chart['date'] = cacheControl.get("Date-Modified")
        chart['expires'] = cacheControl.get("Date-Expires")
        chart['maxage'] = cacheControl.get("Max-Age")
        # lets figure out the content type
        lower_name = chart_name.lower()
        if 'songs' in lower_name :
            chart['type'] = 'Track'
            typeItem =  SingleTrackItem()
        elif 'albums' in lower_name \
            or any(lower_name in s for s in ['soundtracks', 'billboard 200', 'tastemakers']):
            chart['type'] = 'Album'
            typeItem = SingleAlbumItem()
        elif any(lower_name in s for s in ['social 50', 'uncharted']):
            chart['type'] = 'Artist'
            typeItem =  SingleArtistItem()
        else:
            chart['type'] = 'Track'
            typeItem =  SingleTrackItem()
        
        if(chart['id'] == settings["BILLBOARD_DEFAULT_ALBUMCHART"] or chart['id'] == settings["BILLBOARD_DEFAULT_TRACKCHART"]):
            chart['default'] = 1

        chart = self.parse_items(hxs, chart, typeItem)
        # ok, we've prepped the chart container, lets start getting the pages
        if len(next_pages) > 0 :
            next_page = next_pages.popleft()
            request = Request('http://www.billboard.com'+next_page, callback = lambda r: self.parse_page(r, chart, next_pages, typeItem))
            yield request

    def parse_items(self, hxs, chart, typeItem):
        # parse every chart entry
        chart_list = []
        for item in hxs.select('//div[contains(@class,"chart_listing")]/article'):
            loader = XPathItemLoader(typeItem, selector=item)
            loader.add_xpath('rank', 'header/span[contains(@class, "chart_position")]/text()')
            # ptitle yields the title for the type, so just set the title to whatever the chartype is.
            if 'artist' in chart['type'].lower() :
                loader.add_xpath('artist', 'header/p[@class="chart_info"]/a/text()')
            else :
                loader.add_xpath(chart['type'].lower(), 'header/h1/text()')
                loader.add_xpath('artist', 'header/p[@class="chart_info"]/a/text()')
                loader.add_xpath('album', 'header/p[@class="chart_info"]/text()')

            single = loader.load_item()
            chart_list.append(dict(single))
         
        chart['list'] += chart_list

        return chart

    def parse_page(self, response, chart, next_pages, typeItem):
        
        hxs = HtmlXPathSelector(response)
        chart = self.parse_items(hxs, chart, typeItem)

        if len(next_pages) == 0:
            log.msg("Done with %s" %(chart['name']))
            yield chart
        else:
            next_page = next_pages.popleft()
            log.msg("Starting nextpage (%s) of %s - %s left" % (next_page, chart['name'], len(next_pages)))
            request = Request('http://www.billboard.com'+next_page,
                            callback = lambda r: self.parse_page(r, chart, next_pages, typeItem))
            yield request
