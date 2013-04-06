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
from scrapy import log
from scrapers.items import ChartItem, SingleAlbumItem, DetailItem, Detail, slugify
from sources.utils import cache as chartCache
import re
import urllib2



class DjShopSpider(CrawlSpider):
    name = "djshop.de"
    allowed_domains = ["djshop.de"]
    baseUrl = "http://www.djshop.de/"
    baseCharts = [ "%sDownload-Charts/ex/s~mp3,u~charts/xe/Download-Charts.html" % baseUrl,
                   "%sVinyl-Charts/ex/s~charts/xe/charts.html" % baseUrl ]

    chartTypes = [{"unpretty" : "MP3 Downloads Charts", "pretty" : "Digital Charts"}, \
                  {"unpretty" : "Charts Style Charts", "pretty" : "Vinyl Charts"}, \
                  {"unpretty" : "Charts Top 100", "pretty" : "Top 100"}, \
                  {"unpretty" : "Charts International Charts", "pretty" : "International Charts"}]

    # Expires in 2 days
    expires = chartCache.timedeltaUntilDays(2)
    cacheControl = chartCache.setCacheControl(expires)

    source_id = "djshop.de"
    source_name = "djShop.de"
    description = "Updated daily with what's currently hot on the electronic scene."
    have_extra = True
    details = DetailItem(Detail(
        id = source_id, 
        description = description,
        name = source_name,
        have_extra = have_extra
        )
    );

    def __init__(self, name=None, **kwargs):
        super(DjShopSpider, self).__init__()
        chartCache.shoveDetails(self.details)
        self.get_chart_urls()

    def get_chart_urls(self):
        for chart in self.baseCharts:
            req = urllib2.Request(chart)
            hxs = HtmlXPathSelector(text=urllib2.urlopen(req).read())
            try:
                navBox = hxs.select('//div[@id="leftColumn"]')
                navList = navBox.select('//ul[@class="navUL"]/li')
                for index, link in enumerate(navList):
                    if not "Label Charts" in link.select('a/text()').extract()[0].strip():
                        self.start_urls.append("http://www.djshop.de" + link.select('a/@href').extract()[0].strip())
            except Exception, e:
                print e

    def parse(self, response):
        log.msg("Parsing: %s"%(response.url), loglevel=log.INFO)
        hxs = HtmlXPathSelector(response)
        chart = ChartItem()
        title = hxs.select("//title/text()").extract()[0].strip()
        test = re.compile('^(MP3 Downloads(\sCharts|\s))(.*?)(\sCharts)', re.IGNORECASE)

        try:
            cTitle = test.match(title).group(3)
            if cTitle is not None:
                type = self.chartTypes[2]["pretty"]+" ";
                if "vinyl" in response.url.lower() :
                    type += self.chartTypes[1]["pretty"]
                else :
                    type += self.chartTypes[0]["pretty"]
                chart["extra"] = type;
                chart["name"] = cTitle.replace(self.chartTypes[2]["pretty"], "")

        except Exception:
            for type in self.chartTypes:
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
                            chart["extra"] += self.chartTypes[1]["pretty"]
                        else :
                            chart["extra"] += self.chartTypes[0]["pretty"]
                        chart["name"] = chart["name"].replace("Charts", "")

        if "name" in chart :
            chart["name"] = chart["name"].rstrip("-").strip()
            chart['display_name'] = chart["name"] if chart["name"] else "Top Overall"
            chart['origin'] = response.url
            chart['source'] = 'djshop.de'
            chart['id'] = slugify(chart["extra"] + chart["name"])
            chart["type"] = "Album"
            chart['date'] = self.cacheControl.get("Date-Modified")
            chart['expires'] = self.cacheControl.get("Date-Expires")
            chart['maxage'] = self.cacheControl.get("Max-Age")
            chart['list'] = []

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