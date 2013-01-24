#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Casey Link <unnamedrambler@gmail.com>
# Copyright (C) 2012 Hugo Lindström <hugolm84@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
New style charts api.

URL structure:

/charts : contains resources with charts
/charts/<name> : list of charts for a source
/charts/<name>/<id> : chart data for source
"""

#
# local includes
#
from sources.source import Source

# flask includes
#
from flask import Blueprint, make_response, jsonify, request
#
#system
#
import urllib
from pkg_resources import parse_version
charts = Blueprint('charts', __name__)

## Routes and Handlers ##

# 'wearehunted' is removed until we get further information on their api status
# NOTE!!! If new sources isnt backward comp. with > 0.5.9, append to end!!!!
generic_sources = ['itunes', 'billboard', 'rdio', 'ex.fm', 'soundcloudwall', 'hotnewhiphop', 'djshop.de']

sources = { source: Source(source) for source in generic_sources }

# pre 0.5.99 djshop wasnt available, and its not backward comp
# Check version from tomakawk, itunes didnt make it pre 0.5.99
def getSources(request):
    version = str(request.args.get('version'))
    if version is None or parse_version('0.6.99') > parse_version(version) :
        sources = { source: Source(source) for source in generic_sources[:6] }
    else :
        sources = { source: Source(source) for source in generic_sources }
    return sources
    
# Filters out anything thats not geo and/or type
def filterChart(request, chart):
    tmpDict = {}
    geo = request.args.get("geo")
    type = request.args.get("type")

    if geo is None and type is None :
        return chart

    # Could probably have a nice filter here
    for item in chart :
        if geo is not None and type is not None :
            if geo in chart[item]['geo'] and type in chart[item]['type'] :
                tmpDict[item] = chart[item]
        elif geo is not None and type is None:
            if geo in chart[item]['geo'] :
                tmpDict[item] = chart[item]
        elif geo is None and type is not None:
            if type in chart[item]['type'] :
                tmpDict[item] = chart[item]
    return tmpDict

@charts.route('/charts')
def welcome():
    response = make_response( jsonify(
        {
            'sources': getSources(request).keys(),
            'prefix': '/charts/'
        }
    ))
    for sourceName in sources.keys() :
        try :
            response.headers.add(sourceName + 'Expires', sources.get(sourceName, None).get_cacheControl(isChart = True)['Expires'])
        except Exception: 
            print "Cache Error"
    return response
       
@charts.route('/charts/<id>')
def source(id):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    charts = source.chart_list()
    if  charts is None :
        return make_response("Source exist, no charts though", 404)
    for chart in charts:
        charts[chart]['link'] = "/charts/%s/%s" %(id, charts[chart]['id'])

    # filter?
    charts = filterChart(request, charts);

    response = make_response(jsonify(charts))
    cacheControl = source.get_cacheControl(isChart = True)
    for key in cacheControl.keys() :
        response.headers.add(key, cacheControl[key])
    return response

@charts.route('/charts/<id>/<regex(".*"):url>')
def get_chart(id, url):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    url = urllib.unquote_plus(url)
    chart = source.get_chart(url)
    if chart is None:
        return make_response("No such chart", 404)
    response = make_response(jsonify(chart))
    cacheControl = source.get_cacheControl(isChart = True)
    for key in cacheControl.keys() :
        response.headers.add(key, cacheControl[key])
    return response

