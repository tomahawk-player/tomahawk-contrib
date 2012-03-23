#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Casey Link <unnamedrambler@gmail.com>
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

#
# local includes
#
from sources.source import Source

#
# flask includes
#
from flask import Blueprint, Flask, request, session, g, \
                  redirect, url_for, abort, render_template, \
                  flash, make_response, jsonify
from werkzeug.routing import BaseConverter
#
#system
#
import urllib

charts = Blueprint('charts', __name__)

## Routes and Handlers ##

generic_sources = ['itunes', 'billboard','rdio', 'wearehunted', 'ex.fm', 'soundcloudwall']

sources = { source: Source(source) for source in generic_sources }

@charts.route('/charts')
def welcome():
    return jsonify(
        {
            'sources': sources.keys(),
            'prefix': '/charts/'
        }
    )

@charts.route('/charts/<id>')
def source(id):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    charts = source.chart_list()
    for chart in charts:
        charts[chart]['link'] = "/charts/%s/%s" %(id, charts[chart]['id'])

    return jsonify(charts)

@charts.route('/charts/<id>/<regex(".*"):url>')
def get_chart(id, url):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    url = urllib.unquote_plus(url)
    chart = source.get_chart(url)
    if chart is None:
        return make_response("No such chart", 404)
    resp = jsonify(chart)
    return resp

