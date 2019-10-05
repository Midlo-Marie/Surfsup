
# Program to access Honolulu database to return precipitation,
# temperature, and station data for a prescribed period of 
# time
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import Column, Integer, String, Float

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# https://docs.sqlalchemy.org/en/13/core/engines.html provides syntax for SQLAlchemy methods

database_path = "./Resources/hawaii.sqlite"

engine = create_engine(f"sqlite:///{database_path}", connect_args={'check_same_thread': False})


# Reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

lastDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestDate = list(np.ravel(lastDate))[0]

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')
latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
latestDay = int(dt.datetime.strftime(latestDate, '%d'))

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# "Home" Route lists the options for all routes
@app.route("/")
def main():
    # Lists all available routes.
    return (
        f"This api gives you the information about Honolulu weather stations, precipation and temperature"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations  -- A list of all stations and locations<br/>"
        f"/api/v1.0/precipitation -- Rain amounts for previous year <br/>"
        f"/api/v1.0/temperature -- Temperature for the previous year <br/>"
        f"/api/v1.0/start/ <start> (yyy-mm-dd) --  Min, max, average temperatures after given start date <br/>"
        f"/api/v1.0/startend/<start>/<end> --  Input dates from 2010-01-01 to 2017-08-23 <br>")

# "Precipitation" route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the precipitation value
    print("Received precipitation API query") 
        
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)
    
# "Stations" route
@app.route("/api/v1.0/stations")
def stations():

    print("Received station API query") 
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the station data including name and position information with elevation
    all_stations = session.query(Station.name).all()

    # Prepare a list of dictionaries to contain all of the data in column order
    all_stations_list= list(np.ravel(all_stations))

    return jsonify(all_stations_list)


# "Temperature" route
@app.route("/api/v1.0/temperature")
def temperature():
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the temperature value.  Use same logic as precip, change to temperature
    print("Received temperature API query") 
    
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

# "start after" route
@app.route("/api/v1.0/start/<start>")
def start(start):
    # Return a JSON representation of a dictionary where the date is the key and the values are
    # the measurements later than the start date
    print("Received start date API query") 
    query = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  (session.query(*query)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


# "Specific period of time, start and end dates"
@app.route("/api/v1.0/startend/<start>/<end>")
def startend(start, end):
    print("Received start to end date API query")  
    query = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*query)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
