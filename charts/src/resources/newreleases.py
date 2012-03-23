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
"""
New style newreleases api.

URL structure:

/newreleases : contains resources with newreleases
/newreleases/<name> : list of newreleases for a source
/newreleases/<name>/<id> : chart data for source
"""

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

newreleases = Blueprint('newreleases', __name__)

## Routes and Handlers ##

generic_sources = ['rovi']

sources = { source: Source(source) for source in generic_sources }

@newreleases.route('/newreleases')
def welcome():
    return jsonify(
        {
            'sources': sources.keys(),
            'prefix': '/newreleases/'
        }
    )

@newreleases.route('/newreleases/<id>')
def source(id):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    newreleases = source.newreleases_list()
    if newreleases is None:
        return make_response("No new releases", 404)
    for nr in newreleases:
        newreleases[nr]['link'] = "/newreleases/%s/%s" %(id, newreleases[nr]['id'])

    return jsonify(newreleases)

@newreleases.route('/newreleases/<id>/<regex(".*"):url>')
def get_nr(id, url):
    source = sources.get(id, None)
    if source is None:
        return make_response("No such source", 404)
    url = urllib.unquote_plus(url)
    nr = source.get_newreleases(url)
    if nr is None:
        return make_response("No such new release", 404)
    resp = jsonify(nr)
    return resp

