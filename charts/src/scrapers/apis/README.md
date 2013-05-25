Chart Api Scrapers
==============

Sometimes we dont need to scrape HTML for chart sources. If there's an available api, we should use those instead.

Current Apis:

* Rdio
* We Are Hunted
* Rovi (New releases)
* Soundcloudwall
* Ex.fm
* ThisIsMyJam

If you feel there's charts missing here, you can write your own:

Writing API scrapers
---------

Writing a scraper is really easy!

Every scraper needs to inherit the Chart baseclass, and your new scraper needs to have certain attributes to enforce that all sources and charts work the same. The basics are:

    class MyApiScraper(Chart):
        # A source id to identify this source
        source_id = "myapi"
        # This source can have a custom prettyname, or get a title():ed from source_id
        name = "MyApiPrettyName"
        # A description for this source
        description = "MyApi decscription"
        # If this source uses the extra param (Geo/Genre/Arbitrary delimiter)
        have_extra = True/False
        baseUrl = "http://myapi.com"

The baseclass Chart will [Shove][shove] a DetailItem with this information, later accessable via the cache system.
To continue, our new scraper needs to implement the functions init() and parse(), as the baseclass will call these to start the scraping process.

        '''
            Init will be called from Chart
            Here we can set specifics of this source/chart via the set methods from Chart
        '''
        def init(self):
            # For instance, when this chart expires (defaults to 1 day, 1am if not set)
            self.setExpiresInDays(number_of_days)

        '''
            Parse will be called from Chart after init. From here we can implement our parsing logic
        '''
        def parse(self):
            # First lets get the response
            apiResponse = self.getJsonFromResponse(self.baseUrl)

            # Charts can have 3 types, Artist, Track and Album
            self.setChartType(apiResponse["type"])

            # Charts need to have an id, that is unique for this source
            self.setChartId(slugify("%s %s" % (apiResponse['id'], self.chart_type)))

            # Charts also need, display_name, chart_origin, default, and optional geo, genre, extra attributes.
            self.setChartOrigin(self.baseUrl)
            self.setChartName(apiResponse['name'])
            self.setChartDisplayName(self.chart_name)

            # And of course, every chart needs its list of items
            result_list = []
            for rank, item in enumerate(apiResponse['result']):
                # This api only have a Track chart
                chart_item = {
                    'rank' : rank,
                    'artist' : item['artist'],
                    'track' : item['title']
                }
                result_list.append(chart_item)
            # Parsing is done, now store this chart
            self.storeChartItem(result_list)

Furthermore, we need to register this source in ChartDetails class. If it doesnt use any geo/genre/extra attributes, its backward compatible with Tomahawk pre 0.6.1. That means we can add it to __generic_sources, otherwise, just append the source_id to the __generic_non_compatible_sources list.

If all the requirements are met, thats it! Run the scraper and this source together its chartitems should now be accessable from http://localhost:8080/chart/myapi

[shove]: http://pypi.python.org/pypi/shove
