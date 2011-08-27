
import lxml.html
import json
import urllib2
import string

generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'

def get_countries():
    doc = lxml.html.parse(generator_url)

    countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]

    return countries


def get_music_feeds(countries):
    # { name: country, charts: [], genres: [] }
    music_data = []

    for c in countries:
        url = available_url % (c)

        data = urllib2.urlopen(url).read()

        # the response has a jsonp callback, lets remove that
        data = data.replace("availableFeeds=", "")

        j = json.loads(data)
        # there are alot of categories, we just want the ones with music
        for type in j['list']:
            if type['name'] != "Music":
                continue
            # returns a list of tuples, where each tuple
            # contains the genre name and numeric id
            genres = [ (g['value'], g['display'] ) for g in type['genres']['list'] ]
            # returns a list of tuples, where each tuple
            # contains:
            # url suffix (e.g., 'xml')
            # urk prefix
            # name of the feed (e.g, "topalbums")
            # display name of the feed (e.g., "Top Albums")
            charts = [ (c['urlSuffix'], c['urlPrefix'], c['name'], c['display']) for c in type['types']['list'] ]

            music_data.append( { "country":c, "charts": charts, "genres": genres } )

    return music_data

def construct_feeds(music_feeds, limit):
    feeds = []
    for item in music_feeds:
        country = item['country']
        for chart in item['charts']:
            base_url = chart[1]
            suffix = chart[0]
            url = "%s/limit=%s/%s" % (base_url, limit, suffix)
            feeds.append(url)
            for genre in item['genres']:
                g_id = genre[0]
                if len(g_id.strip()) == 0:
                    #sometimes we get blank genres
                    continue
                url = "%s/limit=%s/genre=%s/%s" % (base_url, limit, g_id, suffix)
                feeds.append(url)
    return feeds


def main():
    feeds = construct_feeds(get_music_feeds(get_countries()), 100)
    for f in feeds:
        print f

if __name__ == '__main__':
    main()
