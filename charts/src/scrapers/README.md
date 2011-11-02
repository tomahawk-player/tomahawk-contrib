Chart Scrapers
==============

Here lie the scrapers/spiders for all our sources. It uses the [scrapy screen scraping
framework][scrapy].


Current Spiders:

* Billboard.com - billboard.com
* iTunes Store - itunes.com

Current Apis:
* Rdio.com
* WeAreHunted

Upcoming Spiders:

* The Official Charts - theofficialcharts.com


Get Going for Spiders
---------

1) Install scrapy:

    sudo pip install scrapy

2) Start the scraper with the following where <DOMAIN> is the domain from a source above.

    scrapy crawl <DOMAIN> --set FEED_URI=items.json --set FEED_FORMAT=json &> log


3) tail log, to see the progress.

4) The charts will be in items.json when it completes, as well as in the storage system (see settings.py)

[scrapy]: http://scrapy.org/

Get Going for Apis
---------

1) Cd in the apis folder
2) Run the scripts
3) Finished!