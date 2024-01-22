# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt 
import numpy as np 
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Closing the session as we are creating sessions in each route instead
session.close()

#################################################
# Flask Setup
#################################################
app = Flask (__name__)

#################################################
# Flask Routes
#################################################


# Welcome Page Route
@app.route("/")

def welcome():
    return (
        "<h1>Welcome to my Climate App!</h1>"
        "<p>Here are the available routes:</p>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        "<li><a href ='/api/v1.0/'>/api/v1.0/<a/>(required: Enter start_date as YYYY-MM-DD)/(optional: Enter end_date as YYYY-MM-DD)</li>"
        "</ul>"
    )

# Precipitation Route
@app.route('/api/v1.0/precipitation')

def precipitation():
    
    # Create the session
    session = Session(engine)
    
    # Query Setup
    results = session.query(Measurement.date,Measurement.prcp)\
        .filter(Measurement.date >= dt.date(2017,8,23) - dt.timedelta(days=365))\
            .order_by(Measurement.date).all()
    
    # Close the session
    session.close()

    # Creating an output list
    output = []

    # Iterating through each record in the results list
    for record in results:
        # Empty dictionary for each record
        prcp_dict = {}
        # Assigning attributes of each record to the corresponding dictionary key
        prcp_dict['date'] = record.date
        prcp_dict['prcp'] = record.prcp

        # Appending the dictionary information to the output list above
        output.append(prcp_dict)

    # Jsonifying the output
    return jsonify(output)    


# Stations Route
@app.route('/api/v1.0/stations')
def stations():

    # Create the session
    session = Session(engine)

    # Query Setup
    station_list = session.query(Station.station).all()

    # Close the session
    session.close()

    # Creating an output list
    output = []
    
    # Append each record to the list
    for record in station_list:
        output.append(record.station)
    
    # Jsonifying the output
    return jsonify(output)


# Tobs Route
@app.route('/api/v1.0/tobs')
def tobs():

    # Create the session
    session = Session(engine)

    # Query Setup
    # Added Measurement.station to the query to include the station ID
    temp_stats = session.query(Measurement.station,\
                               func.min(Measurement.tobs),\
                               func.max(Measurement.tobs), \
                               func.avg(Measurement.tobs))\
                               .filter(Measurement.date >= dt.date(2017,8,23) - dt.timedelta(days=365))\
                                 .filter(Measurement.station == 'USC00519281').all()

    # Close the session
    session.close()

    # Creating an output list
    output = []

    # Create a dictionary
    for record in temp_stats:
        temp_dict = {
            'Station ID' : record[0],
            'Min Temp' : record[1],
            'Max Temp' : record[2],
            'Average Temp' : record[3]
        }

        # Append each record to the list
        output.append(temp_dict)

    # Jsonifying the output
    return jsonify(output)    

@app.route('/api/v1.0/<start>')
def temp_stats_start(start):

    # Create the session
    session = Session(engine)

    # Query Setup
    results = session.query(func.min(Measurement.tobs), \
                            func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs)) \
                                .filter(Measurement.date >= start).all()

    # Close the session
    session.close()

    # Create a dictionary
    output = {
        'start_date' : start,
        'TMIN' : results[0][0],
        'TAVG' : results[0][1],
        'TMAX' : results[0][2]
    }

    # Jsonifying the output
    return jsonify(output)

@app.route('/api/v1.0/<start>/<end>')
def temp_stats_range(start,end):

    session = Session(engine)

    # Query Setup
    results = session.query(func.min(Measurement.tobs), \
                            func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs))\
                                .filter(Measurement.date >= start, Measurement.date <= end).all()
    
    # Close the session
    session.close()
    
    # Create a dictionary
    output = {
        'start_date' : start,
        'end_date' : end,
        'TMIN' : results[0][0],
        'TAVG' : results[0][1],
        'TMAX' : results[0][2]
    }

    # Jsonifying the output    
    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)