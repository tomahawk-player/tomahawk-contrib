#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Hugo Lindström <hugolm84@gmail.com>
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


from urlparse import urlparse
from scrapy.conf import settings
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy.item import Item
from scrapy import log
from collections import deque
from scrapers.items import ChartItem, SingleAlbumItem, DetailItem, Detail, slugify
from sources.utils import cache as chartCache
from scrapers.chart import Chart
import re
import urllib2

class MetacriticSpider(CrawlSpider):
    name = "metacritic.com"
    allowed_domains = ["metacritic.com"]
    baseUrl = "http://www.metacritic.com"
    
    genre_nav_xpath = './/ul[@class="genre_nav"]/li'
    types_xpath = './/ul[contains(@class, "tabs")]/li'
    first_nav_xpath = './/ul[contains(@class, "nav_items")]/li'
    current_page_name_xpath = './/ul[contains(@class, "tabs")]/li/span[@class="active"]/span/text()'
    list_xpath = './/ol[contains(@class,"list_product_condensed")]/li'
    next_page_xpath = './/ul[@class="pages"]/li/a/@href'
    coming_soon_table_xpath = './/table[@class="musicTable"]/tr'
    coming_soon_artist_xpath = './/td[@class="artistName"]'
    coming_soon_album_xpath = './/td[@class="albumTitle"]/text()'

    start_urls = ["http://www.metacritic.com/music"]

    rules = [ 
        Rule (SgmlLinkExtractor(allow=("albums/genre/\w+", )
                , deny=("music", "name",)
                , restrict_xpaths=(genre_nav_xpath,)) 
                , callback='parse_page'
                , follow=True),
        Rule (SgmlLinkExtractor(
                deny=("albums/genre/\w+", "name", "music", "coming-soon/(metascore|userscore|name|date)", "new-releases/name")
                , restrict_xpaths=(types_xpath,)) 
                , callback='parse_new_releases'
                , follow=True),
        Rule (SgmlLinkExtractor(
                allow=("albums/release-date", "albums/score",)
                , deny=("feature", "artist", "/\w+/people",)
                , restrict_xpaths=(first_nav_xpath,)) 
                , callback='parse_new_releases'
                , follow=True)
    ]

    # Expires in 2 days
    expires = chartCache.timedeltaUntilDays(1)
    cacheControl = chartCache.setCacheControl(expires)
    source_id = "metacritic"
    source_name = "Metacritic"
    description = "Critically acclaimed and noteworthy music."
    have_extra = True

    details = DetailItem(Detail(
        id = source_id, 
        description = description,
        name = source_name,
        have_extra = have_extra
        )
    );

    def __init__(self, name=None, **kwargs):
        super(MetacriticSpider, self).__init__()
        chartCache.shoveDetails(self.details)
        chartCache.shoveDetails(self.details, False)

    def get_current_genre(self, hxs):
        navList = hxs.select(self.genre_nav_xpath)
        for index, item in enumerate(navList):
            if item.select('.//span'):
                return item.select('.//span/text()').extract()[0].strip()
        return None

    def get_current(self, hxs, chart):
        try:
            active = hxs.select(self.current_page_name_xpath).extract();
            chart["extra"] = active[0].strip()
            chart["name"] = active[1].strip()
            chart["display_name"] = chart["name"];
            chart["id"] = slugify(chart["name"]+chart["extra"])
        except Exception, e:
            if "coming-soon" in chart["origin"]:
                chart["extra"] = "Coming Soon"
                chart["name"] = "By Date"
                chart["display_name"] = chart["name"];
                chart["id"] = slugify(chart["name"]+chart["extra"])
        
        
        
    def create_chart(self, response, name = None, type = None):
        chart = ChartItem(
            origin=response.url,
            source=self.source_id,
            list=[],
            date=self.cacheControl.get("Date-Modified"),
            expires=self.cacheControl.get("Date-Expires"),
            maxage=self.cacheControl.get("Max-Age"),
            type="Album",
            newrls=True if "new-releases" in response.url or "coming-soon" in response.url else False
        );

        if name is not None and type is not None:
            chart["name"] = name
            chart["display_name"] = name
            chart["id"] = slugify(name+type)
            chart["extra"] = type
        return chart

    def parse_coming_soon_items(self, hxs, chart):
        chart_list = [];
        currentSize = len(chart["list"])+1
        for rank, item in enumerate(hxs.select(self.coming_soon_table_xpath)):
            try:
                artistName = item.select(self.coming_soon_artist_xpath+"/text()").extract()[0].strip();
                if not artistName:
                    artistName = item.select(self.coming_soon_artist_xpath+"/a/text()").extract()[0].strip();
                chart_item = SingleAlbumItem(
                    rank=str(rank+currentSize), 
                    artist=artistName, 
                    album=item.select(self.coming_soon_album_xpath).extract()[0].strip()
                );
                chart_list.append(dict(chart_item))
            except Exception, e:
                continue;
        chart["list"] += chart_list;

    def parse_items(self, hxs, chart):
        chart_list = [];
        currentSize = len(chart["list"])+1
        for rank, item in enumerate(hxs.select(self.list_xpath)):
            print item.select('.//span/text()').extract()[1]
            chart_item = SingleAlbumItem(
                rank=str(rank+currentSize), 
                artist=item.select('.//span/text()').extract()[1].strip(), 
                album=item.select('.//a/text()').extract()[0].strip()
            );
            chart_list.append(dict(chart_item))
        chart["list"] += chart_list;


    def parse_new_releases(self, response):
        chart = self.create_chart(response);
        hxs = HtmlXPathSelector(response);
        self.get_current(hxs, chart);

        log.msg("Parsing: %s %s"%(response.url, chart["name"]), loglevel=log.INFO)

        if "coming-soon" in response.url:
            self.parse_coming_soon_items(hxs, chart)
        else:
            self.parse_items(hxs, chart)
        
        yield chart

    def parse_page(self, response):
        hxs = HtmlXPathSelector(response);    
        chart_name = self.get_current_genre(hxs);
        chart_type = "By date" if "date" in response.url else "By metascore" if "metascore" in response.url else "By userscore";
        
        log.msg("Parsing: %s %s (%s)"%(response.url, chart_name, chart_type), loglevel=log.INFO)

        chart = self.create_chart(response, chart_name, chart_type);

        hxs = HtmlXPathSelector(response); 
        self.parse_items(hxs, chart)
        
        next_pages = hxs.select(self.next_page_xpath).extract()[:8];
        next_pages = deque(filter(lambda e: not 'javascript' in e, next_pages))
        if len(next_pages) > 0:
            yield Request("%s%s" % (self.baseUrl, next_pages.popleft()), callback = lambda r: self.parse_next_page(r, chart, next_pages))

    def parse_next_page(self, response, chart, next_pages):
        log.msg("Parsing %s %s" % (response.url, chart["name"]));
        self.parse_items(hxs=HtmlXPathSelector(response), chart=chart);
        if len(next_pages) > 0:
            yield Request("%s%s" % (self.baseUrl, next_pages.popleft()), callback = lambda r: self.parse_next_page(r, chart, next_pages))
        else:
            yield chart
