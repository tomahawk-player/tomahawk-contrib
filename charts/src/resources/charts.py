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
from flask import Blueprint, make_response, jsonify
#
#system
#
import urllib

charts = Blueprint('charts', __name__)

## Routes and Handlers ##

# 'wearehunted' is removed until we get further information on their api status
generic_sources = ['itunes', 'billboard', 'rdio', 'ex.fm', 'soundcloudwall']

sources = { source: Source(source) for source in generic_sources }

@charts.route('/charts')
def welcome():
    response = make_response( jsonify(
        {
            'sources': sources.keys(),
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

