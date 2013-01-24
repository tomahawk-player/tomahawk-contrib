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
from scrapers.items import ChartItem, SingleTrackItem, SingleAlbumItem, SingleArtistItem, slugify
from collections import deque
from sources.utils import cache as chartCache
import re
import urllib2

@chartCache.methodcache.cache('get_chart_url', expire=settings['ITUNES_EXPIRE'])
def get_chart_urls():
    chart_list = []
    for chart in ["http://www.djshop.de/Download-Charts/ex/s~mp3,u~charts/xe/Download-Charts.html", "http://www.djshop.de/Vinyl-Charts/ex/s~charts/xe/charts.html"]:
        print "parsing " + chart
        req = urllib2.Request(chart)
        hxs = HtmlXPathSelector(text=urllib2.urlopen(req).read())
        try:
            navBox = hxs.select('//div[@id="leftColumn"]')
            navList = navBox.select('//ul[@class="navUL"]/li')
            for index, link in enumerate(navList):
                chart_name = link.select('a/text()').extract()[0].strip()
                if not "Label Charts" in chart_name:
                    chart_list.append("http://www.djshop.de" + link.select('a/@href').extract()[0].strip())
        except Exception, e:
            print e
    return chart_list

class DjShopSpider(CrawlSpider):
    name = "djshop.de"
    allowed_domains = ["djshop.de"]
    start_urls = get_chart_urls()
    '''
        Expires tomorrow
    '''
    def get_maxAge(self) :
        today = datetime.utcnow()
        expires = datetime.replace(today +  timedelta(days=1),hour=1, minute=0, second=0)
        maxage = expires-today
        return maxage.seconds
    
    def parse(self, response):
        log.msg("Parsing: %s"%(response.url), loglevel=log.INFO)
        hxs = HtmlXPathSelector(response)

        chart = ChartItem()

        title = hxs.select("//title/text()").extract()[0].strip()
        types = [ {"unpretty" : "MP3 Downloads Charts", "pretty" : "Digital Charts"}, \
                  {"unpretty" : "Charts Style Charts", "pretty" : "Vinyl Charts"}, \
                  {"unpretty" : "Charts Top 100", "pretty" : "Top 100"}, \
                  {"unpretty" : "Charts International Charts", "pretty" : "International Charts"}]

        test = re.compile('^(MP3 Downloads(\sCharts|\s))(.*?)(\sCharts)', re.IGNORECASE)
        try:
            cTitle = test.match(title).group(3)
            if cTitle is not None:
                type = types[2]["pretty"]+" ";
                if "vinyl" in response.url.lower() :
                    type += types[1]["pretty"]
                else :
                    type += types[0]["pretty"]
                chart["extra"] = type;
                chart["name"] = cTitle.replace(types[2]["pretty"], "")
        except Exception:
            for type in types:
                if type["unpretty"] in title :
                    chart["extra"] = type["pretty"]
                    cTitle = title.replace(type["unpretty"], "")
                    if len(cTitle) == 0:
                        chart["name"] = response.url.split('/')[-1].replace(".html", "").title().replace("-", " ");
                    else :
                        chart["name"] = cTitle
                    if "Top 100" in chart["extra"] :
                        chart["extra"] += " "
                        if "vinyl" in response.url.lower() :
                            chart["extra"] += types[1]["pretty"]
                        else :
                            chart["extra"] += types[0]["pretty"]
                        chart["name"] = chart["name"].replace("Charts", "")

        if "name" in chart :
            chart["name"] = chart["name"].rstrip("-").strip()
            chart['origin'] = response.url
            chart['source'] = 'djshop.de'
            chart['id'] = slugify(chart["extra"] + chart["name"])
            chart["type"] = "Album"
            chart['list'] = []
            cacheControl = chartCache.setCacheControl(self.get_maxAge())
            chart['date'] = cacheControl.get("Date-Modified")
            chart['expires'] = cacheControl.get("Date-Expires")
            chart['maxage'] = cacheControl.get("Max-Age")
            
            '''
                This could be transformed into a track chart
                However, theres so many various and compilations
                and I dont think Tomahawk would parse them good.
                Also, its actually a Vinyl chart, so theres no "track"
                ranking involved
            '''
            typeItem = SingleAlbumItem()
            cols = hxs.select('//div[@class="column1"]')
            chart_list = []
            for index, col in enumerate(cols):
                loader = XPathItemLoader(typeItem, selector=col)
                loader.add_xpath('rank', str(index+1))
                loader.add_xpath('artist', "h2/a/text()")
                loader.add_xpath('album', "h3/text()")
                single = loader.load_item()
                chart_list.append(dict(single))
    
            chart['list'] += chart_list
            yield chart