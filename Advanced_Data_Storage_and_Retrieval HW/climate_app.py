#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 08:01:18 2019

@author: dkmacbookpro
"""


import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB

app = Flask(__name__)

@app.route("/")

def home():
    print("Server received request for 'Home' page...")
    
    session = Session(engine)
    query_dates = session.query(Measurement.date).all()
    dates = [date[0] for date in query_dates]
    last_date = max(dates)
    first_date = min(dates)
    
    return (
        f"Welcome to the Climate App by Daniel Kim!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd or /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"Please pick a date between {first_date} and {last_date}"
        )

@app.route("/api/v1.0/stations")

def stations():
    print("Server received request for 'Stations' page...")
    session = Session(engine)
    results = session.query(Measurement.station).distinct(Measurement.station).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")

def tobs():
    print("Server received request for 'Tobs' page...")
    session = Session(engine)

    query_dates = session.query(Measurement.date).all()
    dates = [date[0] for date in query_dates]
    last_date = max(dates)
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d").date()
    one_year_prior = last_date + relativedelta(months=-12)
    last_date = last_date.strftime('%Y-%m-%d')
    one_year_prior = one_year_prior.strftime('%Y-%m-%d')
    
    results = session.query(Measurement.date, Measurement.tobs).filter(and_(Measurement.date <= last_date, Measurement.date >= one_year_prior)).all()

    last_one_year_temp_list = []
    
    for result in results:
        temp_dict = {}
        temp_dict["Date"]= result.date
        temp_dict["Temperature"] = result.tobs
        last_one_year_temp_list.append(temp_dict)
    return jsonify(last_one_year_temp_list)


@app.route("/api/v1.0/<start_date>")

def start_date(start_date):
    session = Session(engine)
    print("Server received request for 'Start_Date' page...")
    
    input_date = start_date
    
    results = session.query(Measurement.date)
    date_list = [x[0] for x in results]
    
    if input_date in date_list:
        
    
        lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= input_date).all()
        highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= input_date).all()
        avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= input_date).all()
        
        return (
            f"The lowest temp is {[x[0] for x in lowest_temp]}.<br/>"
            f"The highest temp is {[x[0] for x in highest_temp]}.<br/>"
            f"The average temp is {[x[0] for x in avg_temp]}<br/>"
            )
    
    if input_date not in date_list:
        return jsonify({"error": f"Date {start_date} out of range. Please pick another date."}), 404


@app.route("/api/v1.0/<start_date>/<end_date>")

def start_and_end_dates(start_date, end_date):
    session = Session(engine)
    print("Server received request for 'Start_Date & End_Date' page...")
    
    
    results = session.query(Measurement.date)
    date_list = [x[0] for x in results]
    
    if start_date in date_list and end_date in date_list:

    
        lowest_temp = session.query(func.min(Measurement.tobs)).filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
        highest_temp = session.query(func.max(Measurement.tobs)).filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
        avg_temp = session.query(func.avg(Measurement.tobs)).filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
        
        return (
            f"The lowest temp is {[x[0] for x in lowest_temp]}.<br/>"
            f"The highest temp is {[x[0] for x in highest_temp]}.<br/>"
            f"The average temp is {[x[0] for x in avg_temp]}<br/>"
            )
    
    if start_date not in date_list or end_date not in date_list:
        return jsonify({"error": f"Date {start_date} or {end_date} out of range. Please pick another dates."}), 404


from flask import request

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

# Lastly, use `if __name__ == "__main__"` to define "main" behavior.

  # `app.run` is all we need to do to start the development server.
  # Passing `debug=True` makes development much easier, but in production,
  # best practices demand that `debug` must **always** be false.

if __name__ == "__main__":
    app.run()