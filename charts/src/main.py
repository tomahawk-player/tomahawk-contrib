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
from resources.charts import charts
from resources.newreleases import newreleases

#
# flask includes
#
from flask import Flask
from werkzeug.routing import BaseConverter

#
# twisted is our new web backend
#
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
# Twisted logging
import sys
from twisted.python import log
from twisted.python.logfile import DailyLogFile

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

# custom url converter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

app.register_blueprint(charts)
app.register_blueprint(newreleases)

if __name__ == '__main__':
    if DEBUG :
        log.startLogging(sys.stdout)
        log.startLogging(DailyLogFile.fromFullPath("logs/charts-twisted.log"))
    # Start the service
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    reactor.listenTCP(8080, Site(resource), interface="127.0.0.1")
    reactor.run()
