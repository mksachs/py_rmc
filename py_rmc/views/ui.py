import py_rmc.data.models
from py_rmc import rmc

import flask

import json
import pprint


@rmc.route('/encounters', methods=['get'])
def encounters_ui():
    return flask.render_template('encounters.html', test='test')


@rmc.route('/encounters/<encounter_id>', methods=['get'])
def encounter_ui(encounter_id):
    return flask.render_template('encounter.html', encounter_id=encounter_id)
