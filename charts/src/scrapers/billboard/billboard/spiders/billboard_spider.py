from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from billboard.items import ChartItem, SingleItem


from collections import deque

class BillboardSpider(CrawlSpider):
    name = "billboard.com"
    allowed_domains = ["billboard.com"]
    start_urls = [
        #"http://www.billboard.com/charts/hot-100"
        "http://www.billboard.com/charts"
    ]

    chart_xpath = '//div[@class="units"]/ul/li/div[@class="chart"]/h2/a'
    next_page_xpath = '//div[@class="pagination-group"]/ul/li/a/@href'
    rules = [
        #Rule(SgmlLinkExtractor(allow=['\?begin=\d+']), 'parse_chart'),
        Rule(SgmlLinkExtractor(allow=['/charts/\w+'], restrict_xpaths=chart_xpath), callback='parse_chart', follow=True)
    ]

    crawled = set()

    def parse_chart(self, response):
        hxs = HtmlXPathSelector(response)

        next_pages = hxs.select(self.next_page_xpath).extract()
        next_pages = deque(filter(lambda e: not 'javascript' in e, next_pages))
        chart_name = hxs.select('//*[@class="printable-chart-header"]/h1/b/text()').extract()[0]

        chart = ChartItem()
        print "making NEW chart"
        chart['name'] = chart_name
        chart['origin'] = response.url
        chart['list'] = []

        next_page = next_pages.popleft()

        request = Request('http://www.billboard.com'+next_page, callback = lambda r: self.parse_page(r, chart, next_pages))

        yield request

    def parse_page(self, response, chart, next_pages):
        hxs = HtmlXPathSelector(response)
        chart_name = hxs.select('//*[@class="printable-chart-header"]/h1/b/text()').extract()[0]
        list = []
        for item in  hxs.select('//*[@class="printable-row"]'):
            loader = XPathItemLoader(SingleItem(), selector=item)
            loader.add_xpath('rank', 'div/div[@class="prank"]/text()')
            loader.add_xpath('track', 'div/div[@class="ptitle"]/text()')
            loader.add_xpath('artist', 'div/div[@class="partist"]/text()')
            loader.add_xpath('album', 'div/div[@class="palbum"]/text()')

            single = loader.load_item()
            list.append(dict(single))

        b4 = len(chart['list'])
        chart['list'] += list
        print "got EXISTING chart: "
        print b4, len(list), len(chart['list'])

        if len(next_pages) == 0:
            print "Done with %s" %(chart_name)
            yield chart
        else:
            next_page = next_pages.popleft()
            print "Starting nextpage (%s) of %s - %s left" %(next_page, chart_name, len(next_pages))
            request = Request('http://www.billboard.com'+next_page, callback = lambda r: self.parse_page(r, chart, next_pages))

            yield request
