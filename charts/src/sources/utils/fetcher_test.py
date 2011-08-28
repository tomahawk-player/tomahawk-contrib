import url_fetcher



urls = [
    "http://google.com",
    "http://yahoo.com",
    "http://itunes.apple.com/us/rss/topalbums/limit=10/xml",
    "http://itunes.apple.com/us/rss/topalbums/limit=10/json",
    "http://reddit.com"
]


def process(resp, content):
    if resp.fromcache:
        print "Fetch result %s (cached)" % (resp.status)
    else:
        print "Fetch result %s" % (resp.status)

url_fetcher.start_job(urls, process)
