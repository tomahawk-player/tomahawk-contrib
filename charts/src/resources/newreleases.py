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
New style newreleases api.

URL structure:

/newreleases : contains resources with newreleases
/newreleases/<name> : list of newreleases for a source
/newreleases/<name>/<id> : chart data for source
"""

# local includes
#
from sources.source import Source
# flask includes
#
from flask import Blueprint, make_response, jsonify, request, Response
#system
#
import urllib
from pkg_resources import parse_version
## Routes and Handlers ##
newreleases = Blueprint('newreleases', __name__)
generic_sources = ['rovi', "itunes"]

# pre 0.5.99 rovi is the only available source
# Check version from tomakawk, itunes didnt make it pre 0.5.99
def getSources(request):
    version = str(request.args.get('version'))
    if version is None or parse_version('0.5.99') > parse_version(version) :
        sources = { 'rovi': Source('rovi') }
    else :
        sources = { source: Source(source) for source in generic_sources }
    return sources

@newreleases.route('/newreleases')
def welcome():
    jsonContent = jsonify(
        {
            'sources': getSources(request).keys(),
            'prefix': '/newreleases/'
        }
    )
    response = make_response(jsonContent)
    try:
        for sourceName in getSources(request).keys() :
            response.headers.add(sourceName + "Expires", int(getSources(request).get(sourceName, None).get_cacheControl()["Expires"]))
    except Exception :
        print "Cache Error"
    return response

@newreleases.route('/newreleases/<id>')
def source(id):
    source = getSources(request).get(id, None)
    if source is None:
        return make_response("No such source", 404)
    newreleases = source.newreleases_list()
    if newreleases is None:
        return make_response("No new releases", 404)
    # Check version from tomakawk, editorials didnt make it to pre 0.5.99
    version = request.args.get("version")
    if version is None or parse_version('0.5.99') > parse_version(version) :
        metadata_keys = filter(lambda k: not "editorial" in k, newreleases)
        newreleases = { key: newreleases[key] for key in metadata_keys }
    for nr in newreleases:
        newreleases[nr]['link'] = "/newreleases/%s/%s" %(id, newreleases[nr]['id'])

    response = make_response(jsonify(newreleases))
    for key in source.get_cacheControl().keys() :
        response.headers.add(key, source.get_cacheControl()[key])
    return response

@newreleases.route('/newreleases/<id>/<regex(".*"):url>')
def get_nr(id, url):
    source = getSources(request).get(id, None)
    if source is None:
        return make_response("No such source", 404)
    url = urllib.unquote_plus(url)
    newrelease = source.get_newreleases(url)
    if newrelease is None:
        return make_response("No such new release", 404)

    response = make_response(jsonify(newrelease))
    for key in source.get_cacheControl().keys() :
        response.headers.add(key, source.get_cacheControl()[key])
    return response

