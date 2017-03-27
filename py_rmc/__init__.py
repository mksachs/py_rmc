from flask import Flask

rmc = Flask(__name__)

import py_rmc.views.api
import py_rmc.views.ui