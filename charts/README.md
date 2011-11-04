# Charts Service

Scrapes, fetches, sucks, and caches charts from various sources then spits
out nicely formated XML/JSON for consumption.

We strive to be a polite consumer in our scraping and feed fetching. We don't want to be pissing anybody off.

## The Low Down

The charts service consists of three distinct components:

 1. The scrapers in `src/scrapers`
 2. The HTTP service that provides a REST API in `src/charts.py`
 3. The storage backend (aka, the cache) in `src/sources/utils/cache.py`


### Scrapers

The scrapers parse and format charts data from various services (itunes,
billboard, etc)

See `src/scrapers/README.md`.

### HTTP Service

Mostly contained in `src/charts.py`, but uses some data structures from
`src/sources`.

It uses the [Flask][flask] python microframework to serve an HTTP API.  Flask
has its own builtin webserver, which we proxy using nginx (see
`infrastructure/nginx/`)

### Storage Backend

The storage backend is currently [Shove][shove], a simple object storage
frontend for various storage backends. We currently use the Filesystem storage
module, and store the data in `/tmp/charts`, but in the future we could switch
to one of the many other Shove supported backends (e.g., Postgres, redis,
Amazon s3).

The storage api is a basic key-value store. You put objects in by key, and get
them back with the same key.


## Setup

Install pip, the python packge tool:

    sudo aptitude install python-pip
    OR
    sudo pacman -S python2-pip
    OR
    sudo zypper install python-pip
    
Install dependencies:

    pip install -U -r requirements.txt


[flask]: http://flask.pocoo.org/
[shove]: http://pypi.python.org/pypi/shove
