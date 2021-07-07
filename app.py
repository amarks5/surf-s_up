#import dependencies
import datetime as dt
import numpy as np
import pandas as pd
#import sqlalchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#import flask dependencies - always after sqlalchemy dependencies
from flask import Flask, jsonify

#set up database engine for flask application
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect database into our classes
Base = automap_base()

#reflect the database
Base.prepare(engine, reflect=True)

#save references for each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session link from python to database
session = Session(engine)

#define Flask app
#create Flask app called app
app = Flask(__name__)

#create routes
@app.route("/")
#create function welcome
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calc date one year from most recent date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #write query to get date and precipitation from previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#create stations route
@app.route("/api/v1.0/stations")
def stations():
    #create query to get all stations in database
    results = session.query(Station.station).all()
    #unravel results into 1-dimensional array
    stations = list(np.ravel(results))
    #return as JSON file
    return jsonify(stations=stations)

#create temperature route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #create query of primary station for all temp observations from previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
        #convert array to list
    temps = list(np.ravel(results))
    #return as JSON file
    return jsonify(temps=temps)

#create statistics route !DIFFERENT! ***NEED TO ADD START AND END DATE***
@app.route("/api/v1.0/temp_<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
#need parameters for stats() start and end parameter
def stats(start=None, end=None):
    #create query to select min,avg, max temps - list name is sel
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #create if-not statement because we didn't determine start and end date
    if not end:
        #*sel indicates there are multiple results for one query: min,avg,max
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()  
        #unravel the results into one-dimensional array and convert to list
        temps = list(np.ravel(results))
        #JSONIFY file
        return jsonify(temps)
    #calculate temp min, avg, max with start and end dates
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
