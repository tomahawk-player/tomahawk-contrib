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
/charts/detailed : get detailed information about sources
"""

#
# local includes
#
from chartdetails import ChartDetails
from sources.utils import cache as cache
details = ChartDetails();

# flask includes
#
from flask import Blueprint, make_response, jsonify, request

#
#system
#
import urllib
charts = Blueprint('charts', __name__)

## Routes and Handlers ##

@charts.route('/charts/detailed')
def detailed():
    sources = details.getSources(request)
    response = make_response( jsonify(
        {
            'sources': details.getDetails(request),
            'prefix': '/charts/'
        }
    ))
    response = cache.appendExpireHeaders(request, sources, response);
    return response

@charts.route('/charts')
def welcome():
    sources = details.getSources(request)
    response = make_response( jsonify(
        {
            'sources': sources.keys(),
            'prefix': '/charts/'
        }
    ))
    response = cache.appendExpireHeaders(request, sources, response);
    return response

@charts.route('/charts/<id>')
def source(id):
    sources = details.getSources(request)
    source = sources.get(id, None)

    if source is None:
        return make_response("No such source, from %s" % sources, 404)

    charts = source.chart_list()

    if  charts is None :
        return make_response("Source exist, no charts though", 404)

    for chart in charts:
        try:
            charts[chart]['link'] = "/charts/%s/%s" %(id, charts[chart]['id'])
        except Exception, e:
            print "Source error: %s" % e
        
    # No geo in rdio, pre 0.6.99
    if not details.backwardComp(request.args) and "rdio" in id:
        charts = details.filterChart({"geo" : "US", "version" : request.args.get("version")}, charts);

    # filter?
    charts = details.filterChart(request.args, charts);

    # Append details?
    charts.update(details.getDetail(request, id));

    response = make_response(jsonify(charts))
    response = cache.appendCacheHeader(source, response)

    return response

@charts.route('/charts/<id>/<regex(".*"):url>')
def get_chart(id, url):
    sources = details.getSources(request)
    source = sources.get(id, None)

    if source is None:
        return make_response("No such source", 404)

    url = urllib.unquote_plus(url)
    chart = source.get_chart(url)

    if chart is None:
        return make_response("No such chart", 404)

    response = make_response(jsonify(chart))
    response = cache.appendCacheHeader(source, response)
    return response

