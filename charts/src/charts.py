#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
