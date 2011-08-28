Billboard.com Scraper
=====================

A scraper for Billboard.com's music charts. It uses the [scrapy screen scraping
framework][scrapy].


Get Going
---------

1) Install scrapy:

    sudo pip install scrapy

2) Start the scraper with:

    scrapy crawl billboard.com --set FEED_URI=items.json --set FEED_FORMAT=json &> log

3) tail log, to see the progress.

4) The charts will be in items.json when it completes

[scrapy]: http://scrapy.org/
