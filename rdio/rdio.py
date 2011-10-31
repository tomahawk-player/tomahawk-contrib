#!/usr/bin/env python2
import sys,os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import web, urllib
import oauth2 as oauth

urls = (
  '/(.*)', 'root',
)
app = web.application(urls, globals())

class root:
  def GET(self, url):
    
      consumer = oauth.Consumer('gk8zmyzj5xztt8aj48csaart', 'yt35kakDyW')
      client = oauth.Client(consumer)
      response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'getObjectFromUrl', 'url': url, 'extras': 'tracks'}))
      return response[1]

if __name__ == "__main__":
    app.run()
