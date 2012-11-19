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

import datetime
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
    chart_xpath = '//div[@class="units"]/ul/li/div[@class="chart"]/h2/a'
    # the xpath to the pagination links
    next_page_xpath = '//div[@class="pagination-group"]/ul/li/a/@href'

    # we only need one rule, and that is to follow
    # the links from the charts list page
    rules = [
        Rule(SgmlLinkExtractor(allow=['/charts/\w+'], restrict_xpaths=chart_xpath), callback='parse_chart', follow=True)
    ]

    def parse_chart(self, response):
        hxs = HtmlXPathSelector(response)

        chart_name = hxs.select('//*[@class="printable-chart-header"]/h1/b/text()').extract()[0].strip()
        chart_type = hxs.select('//*[@id="chart-list"]/div[@id="chart-type-fb"]/text()').extract()[0].strip()

        # get a list of pages
        next_pages = hxs.select(self.next_page_xpath).extract()
        # remove javascript links and turn it into a queue, also, we want to exclude next chart (!)
        next_pages = deque(filter(lambda e: not 'javascript' or slugify(chart_name) in e, next_pages))

        # Correct the grammar to fit our expectations
        if chart_name == 'Germany Songs':
            chart_name = 'German Tracks'
        
        chart = ChartItem()
        chart['name'] = chart_name
        chart['origin'] = response.url
        chart['source'] = 'billboard'
        chart['id'] = slugify(chart_name)
        today = datetime.datetime.today()
        rd=reldate.relativedelta(weekday=reldate.TH(+1),hours=+21)
        rd2=reldate.relativedelta(hour=13,minute=0,second=0,microsecond=0)
        expires = today+rd+rd2
        chart['date'] = today.strftime("%a, %d %b %Y %H:%M:%S +0000")
        chart['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S +0000")
        maxage = expires-today
        chart['maxage'] = maxage.seconds
        chart['list'] = []

        # lets figure out the content type
        lower_name = chart_name.lower()
        if chart_type == 'Albums' or 'albums' in lower_name or 'soundtrack' in lower_name:
            chart['type'] = 'Album'
            chart['typeItem'] = SingleAlbumItem()
        elif chart_type == 'Artists' or 'artists' in lower_name:
            chart['type'] = 'Artist'
            chart['typeItem'] = SingleArtistItem()
        else:
            chart['type'] = 'Track'
            chart['typeItem'] = SingleTrackItem()
        
        if(chart['id'] == settings["BILLBOARD_DEFAULT_ALBUMCHART"] or chart['id'] == settings["BILLBOARD_DEFAULT_TRACKCHART"]):
            chart['default'] = 1

        # ok, we've prepped the chart container, lets start getting the pages
        next_page = next_pages.popleft()

        request = Request('http://www.billboard.com'+next_page, callback = lambda r: self.parse_page(r, chart, next_pages))

        yield request

    def parse_page(self, response, chart, next_pages):
        
        hxs = HtmlXPathSelector(response)

        # parse every chart entry
        chart_list = []
        for item in hxs.select('//*[@class="printable-row"]'):
            loader = XPathItemLoader(chart["typeItem"], selector=item)
            loader.add_xpath('rank', 'div/div[@class="prank"]/text()')
            # ptitle yields the title for the type, so just set the title to whatever the chartype is.
            loader.add_xpath(chart['type'].lower(), 'div/div[@class="ptitle"]/text()')
            loader.add_xpath('artist', 'div/div[@class="partist"]/text()')
            loader.add_xpath('album', 'div/div[@class="palbum"]/text()')

            single = loader.load_item()
            chart_list.append(dict(single))
            
        chart['list'] += chart_list

        if len(next_pages) == 0:
            log.msg("Done with %s" %(chart['name']))
            yield chart
        else:
            next_page = next_pages.popleft()
            log.msg("Starting nextpage (%s) of %s - %s left" % (next_page, chart['name'], len(next_pages)))
            request = Request('http://www.billboard.com'+next_page,
                            callback = lambda r: self.parse_page(r, chart, next_pages))
            yield request
