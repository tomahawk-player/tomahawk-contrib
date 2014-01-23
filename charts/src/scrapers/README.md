Chart Scrapers
==============

Here lie the scrapers/spiders for all our sources. It uses the [scrapy screen scraping
framework][scrapy].


Current Spiders:

* Billboard.com - billboard.com
* iTunes Store - itunes.com

Current Apis:
* Rdio.com
* Reddit.com
* Soundcloudwall
* Rovi
* Ex.fm
* ThisIsMyJam

Upcoming Spiders:

* The Official Charts - theofficialcharts.com

Disabled:

* WeAreHunted


Get Going for Spiders
---------

1) Install scrapy:

    sudo pip install scrapy

2) Start the scraper with the following where <DOMAIN> is the domain from a source above.

    scrapy crawl <DOMAIN> --set FEED_URI=items.json --set FEED_FORMAT=json &> log

The `--set FEED_URI=items.json` is optional, it just outputs the parsed and formatted results to a json file. 

3) tail log, to see the progress.

4) When complete the results will be in the items.json file, as well as stored in the storage system. 
The storage system currently is a simple file-based [Shove][shove] store. See `src/sources/README/md` for 
information on the storage system.

Interesting Scrapy Code
-----------------------

 * `scrapers/spiders/*_spider.py` - the service specific spiders. These modules know how to parse information from a chart service.
 * `scrapers/pipelines.py` - data parsed from the spiders is fed through this pipeline, which normalizes the data and stores it in the storage system. shared across all spiders.
 * `scrapers/items.py` - the data structures used for parsing out charts data, shared across all spiders

[scrapy]: http://scrapy.org/
[shove]: http://pypi.python.org/pypi/shove

Get Going for Apis
---------

1) Cd in the apis folder
2) Run the scripts
3) Finished!
