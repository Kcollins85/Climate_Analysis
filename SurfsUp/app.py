# Import dependancies
import numpy as np
from datetime import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask
from flask import Flask, jsonify

# Create engine to the database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with = engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)

# Start at the homepage.
# List all the available routes.
@app.route("/")
def welcome():
    return (
        f"Welcome to my Home Page!<br/>"
        f"Available Routes:<br/>"
        f"Precipiation Totals: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation</a><br/>"
        f"Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations</a><br/>"
        f"Daily Temperature Observations for Station USC00519281: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs</a><br/>"
        f"Temperature stats from user defined start date: /api/v1.0/yyyy-mm-dd <br/>"   
        f"Temperature stats from user defined start date to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>" 
        f"<br/>"
        f"<b>PLEASE NOTE:<br/>"
        f"For the temperature stat queries, you enter your own date/date range.<br/>" 
        f"Please input the date selection into the website address instead of the placeholder characters.  Note that dates must be in ISO date format(YYYY-MM-DD). <br/>"        
        f"You can select date ranges between 2010-01-01 and 2017-08-23."  
    )

# Precipitation
# Convert the query results to a dictionary by using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Open the session
    session = Session(engine)

    # Create the date variable
    start_date = "2016-08-23"
    
    # Create a list to hold sum of precipitation score
    sum_prcp = [Measurement.date, func.sum(Measurement.prcp)]

    # Start the query
    prcp_results = session.query(*sum_prcp).filter(Measurement.date >= start_date).group_by(Measurement.date).all()

    # Close the session
    session.close()
    
    # Convert results to a dictionairy
    results_dict = {}
    for date, prcp in prcp_results:
        results_dict[date] = prcp    
        
    # Jsonify the results
    return jsonify(results_dict)  

# Stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    # Open the session
    session = Session(engine)

    # Bring back the station names
    stations = session.query(Station.station).distinct().all()

    # Close the session
    session.close()
    
    # Convert results to a dictionairy
    station_dict = {"stations": [station[0] for station in stations]}

    # Jsonify the results
    return jsonify(station_dict)

# TOBS
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Open the session
    session = Session(engine)

    # Create the variables
    station = "USC00519281"
    start_date = "2016-08-18"

    # Start the query
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date, Measurement.station == station).all()

    # Close the session
    session.close()

    # Convert results to a dictionairy
    tobs_dict = {}
    for date, tobs in tobs_results:
        tobs_dict[date] = tobs

    # Jsonify the results
    return jsonify(tobs_dict)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def get_start(start):
    # Open the session
    session = Session(engine)  

    # Define the start date    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    # Close the session
    session.close()

    # Convert results to a dictionairy
    result_dict = {"Lowest temperature": results[0][0], "Highset temperature": results[0][1], "Average temperature": results[0][2]}

    # Jsonify the list
    return jsonify(result_dict)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
# # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>/<end>")
def get_start_end(start, end):
    # Open the session
    session = Session(engine)  

    # Define the start date and end date  
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.tobs <= end).all()

    # Close the session
    session.close()

    # Convert results to a dictionairy
    start_end_result_dict = {"Lowest temperature": results[0][0], "Highset temperature": results[0][1], "Average temperature": results[0][2]}

    # Jsonify the list
    return jsonify(start_end_result_dict)

# execute the code
if __name__ == "__main__":
    app.run(debug=True)