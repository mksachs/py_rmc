import py_rmc.data.models
from py_rmc import rmc

import flask

import json
import pprint


@rmc.route('/test', methods=['get'])
def test():
    return flask.render_template('test.html', test='test')
