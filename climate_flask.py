
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

engine = create_engine(f"sqlite:///{database_path}")


# Reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# This function called `calc_temps` from the Climate data exercise will accept start date and end date 
# in the format '%Y-%m-%d' and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    # TMIN, TAVG, and TMAX for a list of dates.
    
    # Args:
    #     start_date (string): A date string in the format %Y-%m-%d
    #     end_date (string): A date string in the format %Y-%m-%d
        
    # Returns:
    #     TMIN, TAVE, and TMAX
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    # function usage example
#print(calc_temps('2012-02-28', '2012-03-05'))


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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# "Precipitation" route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the precipitation value
    print("Received precipitation API query") 
    final_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    #set beginning of search query
    begin_date = max_date - dt.timedelta(366)

    #find dates and precipitation amounts
    precip_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()
    
    #prepare the dictionary with the date as the key and the prcp value as the value
    results_dict = {}
    for result in precip_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)

    
# "Stations" route
@app.route("/api/v1.0/stations")
def stations():

    print("Received station API query") 
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the station data including name and position information with elevation
    all_stations = session.query(Station).all()

    # Prepare a list of dictionaries to contain all of the data in column order
    all_stations_list=[]
    for station in all_stations:
        stn_dict = {}
        stn_dict["id"] = station.id
        stn_dict["station"] = station.station
        stn_dict["name"] = station.name
        stn_dict["latitude"] = station.latitude
        stn_dict["longitude"] = station.longitude
        stn_dict["elevation"] = station.elevation
        all_stations_list.append(stn_dict)

    return jsonify(all_stations_list)


# "Temperature" route
@app.route("/api/v1.0/temperatures")
def temperature():
    # Return a JSON representation of a dictionary where the date is the key and the value is 
    # the temperature value
    print("Received temperature API query") 

# "start after" route
@app.route("/api/v1.0/start date")
def start():
    # Return a JSON representation of a dictionary where the date is the key and the values are
    # the measurements later than the start date
    print("Received start date API query") 

# "Specific period of time, start and end dates"
@app.route("/api/v1.0/<start>/<end>")
def time_period(start, end):
    print("Received start to end date API query")  


if __name__ == "__main__":
    app.run(debug=True)
