
import lxml.html
import json
import urllib2
import string

generator_url = 'http://itunes.apple.com/rss/generator/'
available_url = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/wa/RSS/wsAvailableFeeds?cc=%s'
doc = lxml.html.parse(generator_url)


countries = [c.attrib['value'] for c in doc.xpath("//select[@id='feedCountry']/option")]

music_data = []

# { name: country, charts: [], genres: [] }

for c in countries:

    url = available_url % (c)

    data = urllib2.urlopen(url).read()
    data = data.replace("availableFeeds=", "")
    j = json.loads(data)
    for type in j['list']:
        name = type['name']
        if name != "Music":
            continue
        print  "%s has Music!" %(c)
        genres = [ (g['value'], g['display'] ) for g in type['genres']['list'] ]
        charts = [ (c['urlSuffix'], c['urlPrefix'], c['name'], c['display']) for c in type['types']['list'] ]

        music_data.append( { "name":c, "charts": charts, "genres": genres } )

