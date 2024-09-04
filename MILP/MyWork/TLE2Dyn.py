from skyfield.api import load, EarthSatellite, Topos
from datetime import datetime, timedelta

# Load timescale and satellite data
ts = load.timescale()
satellite = EarthSatellite(
    "1 25544U 98067A   22275.65850694  .00006483  00000+0  12600-3 0  9992",
    "2 25544  51.6433 310.0657 0004787 131.8502 345.0242 15.50395232368699",
    "ISS", ts
)

# Define observer's location (example: New York City)
observer_location = Topos(latitude_degrees=40.7128, longitude_degrees=-74.0060)

# Define the time range
start_time = ts.now()
end_time = start_time + timedelta(seconds=10)  # Propagate for 10 seconds

# Convert Skyfield Time to datetime for easier comparison
start_datetime = start_time.utc_datetime()
end_datetime = end_time.utc_datetime()

# Iterate through each second in the time range
current_datetime = start_datetime
while current_datetime <= end_datetime:
    # Convert current_datetime back to Skyfield Time
    current_time = ts.utc(current_datetime.year, current_datetime.month, current_datetime.day,
                          current_datetime.hour, current_datetime.minute, current_datetime.second)

    # Compute the satellite's position
    position = satellite.at(current_time)

    # Compute subpoint (latitude, longitude)
    subpoint = position.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees

    # Define the observer's position and compute the altitude and azimuth
    observer = observer_location.at(current_time)
    difference = position - observer
    alt, az, _ = difference.altaz()
    altitude = alt.degrees


    # Print the results
    print(
        f"Time: {current_time.utc_iso()} -> Latitude: {latitude:.2f}°, Longitude: {longitude:.2f}°, Altitude: {altitude:.2f}°")

    # Increment time by 1 second
    current_datetime += timedelta(seconds=1)

    # Check if the satellite is above the horizon
    visible = altitude > 0

    # Print results
    visibility_status = "Visible" if visible else "Not Visible"
    print(f"Time: {current_time.utc_iso()} -> Latitude: {latitude:.2f}°, Longitude: {longitude:.2f}°, "
          f"Satellite Altitude: {altitude:.2f}°, Target Altitude: {altitude:.2f}°, "
          f"Visibility: {visibility_status}")

    # Increment time by 1 second
    current_datetime += timedelta(seconds=1)

""""# Using sgp4 library
# This method is best used for relatively short-term predictions from the TLE epoch
# sgp4: primarily focuses on propagating satellite orbits using TLE data
from sgp4.api import Satrec
from sgp4.conveniences import jday_datetime
from datetime import datetime, timedelta

# Example TLE from Celestrak
tle_line1 = "1 25544U 98067A   22275.65850694  .00006483  00000+0  12600-3 0  9992"
tle_line2 = "2 25544  51.6433 310.0657 0004787 131.8502 345.0242 15.50395232368699"

# Define observer's location
observer = Topos('40.7128 N', '74.0060 W')

# Create satellite record
satellite = Satrec.twoline2rv(tle_line1, tle_line2)

# Choose a start time and step through each second
start_time = datetime.utcnow() # representing the current UTC time
for i in range(10):  # Change 10 to however many seconds you want to propagate
    time = start_time + timedelta(seconds=i)
    jd, fr = jday_datetime(time)  # Julian date
    e, r, v = satellite.sgp4(jd, fr)  # r and v are the position and velocity vectors
    if e == 0:
        print(f"Time: {time} -> Position (km): {r}, Velocity (km/s): {v}")
    else:
        print(f"Propagation error with code {e}")


 ####### CALCULATE OBSERVATION WINDOW #######
# Load timescale and satellite data
ts = load.timescale()
t0 = ts.now()
t1 = ts.utc(t0.utc_datetime() + timedelta(days=1))  # One day from now

satellite1 = EarthSatellite(tle_line1, tle_line2, 'ISS', ts)

# Calculate satellite passes over the observer
satellite_passes = satellite1.find_events(observer, t0, t1, altitude_degrees=10.0)

# Print the observation windows
for time, event in satellite_passes:
    name = ('rise above 10°', 'culminate', 'set below 10°')[event]
    print(f"{name} at {time.utc_datetime()} UTC") 

"""
 
