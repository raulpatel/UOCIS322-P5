"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
import os
from flask import request, redirect, url_for, request
from pymongo import MongoClient
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404

@app.route('/submit/', methods=['POST'])
def submit():
    item_doc = {
        'km': request.form['km'],
        'open': request.form['open'],
        'close': request.form['close'],
        #'body': request.form['body']
    }
    if item_doc['km'] != "":
        db.tododb.insert_one(item_doc)

    return redirect(url_for('/_calc_times'))

@app.route('/display/', methods=['POST'])
def display():
    item_doc = db.tododb.find_one()
    print(item_doc)

    return redirect(url_for('/'))

###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float) // 1
    start = request.args.get('start')
    brev_dist = request.args.get('brev_dist', type=int)
    app.logger.debug("km={}".format(km))
    app.logger.debug("start={}".format(start))
    app.logger.debug("brev_dist={}".format(brev_dist))
    app.logger.debug("request.args: {}".format(request.args))
    valid = 1
    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    if km <= (brev_dist * 1.2):
        open_time = acp_times.open_time(km, int(brev_dist), arrow.get(start)).format('YYYY-MM-DDTHH:mm')
        close_time = acp_times.close_time(km, int(brev_dist), arrow.get(start)).format('YYYY-MM-DDTHH:mm')
    else:
        valid = 0
        open_time = ""
        close_time = ""
    result = {"valid": valid, "open": open_time, "close": close_time}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
