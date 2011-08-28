#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Casey Link <unnamedrambler@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# local includes
#
from sources import itunes

# flask includes
from flask import Flask, request, session, g, \
                  redirect, url_for, abort, render_template, \
                  flash, make_response, jsonify

#
#system
import urllib

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)


## Routes and Handlers ##

itunes_source = itunes.iTunesSource()

@app.route('/')
def welcome():
    feeds = itunes_source.chart_list()
    resp = ''
    for f in feeds:
       resp += '<a href="/feed/%s">%s</a><br />\n' % (urllib.quote_plus(f), f)
    return resp

@app.route('/feed/<path:url>')
def get_chart(url):
    print url
    real_url = urllib.unquote_plus(url)
    resp = jsonify(itunes_source.get_chart(real_url))
    return resp

if __name__ == '__main__':
    app.run(port=8080)
