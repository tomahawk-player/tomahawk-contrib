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


# flask includes
from flask import Flask, request, session, g, \
                  redirect, url_for, abort, render_template, \
                  flash, make_response

app = Flask(__name__)
app.config.from_object(__name__)


## Routes and Handlers ##

@app.route('/')
def welcome():
    return "Hello World :)";

if __name__ == '__main__':
    app.run(port=8080)
