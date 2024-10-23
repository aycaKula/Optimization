from skyfield.api import Topos, load
from skyfield.api import EarthSatellite
from datetime import datetime, timedelta

# Load satellite TLE data
#tle_line1_sat1 = "1 25544U 98067A   22275.65850694  .00006483  00000+0  12600-3 0  9992"  # ISS
#tle_line2_sat1 = "2 25544  51.6433 310.0657 0004787 131.8502 345.0242 15.50395232368699"

# tle_line1_sat2 = "1 20580U 90037B   22275.54851226  .00000222  00000+0  12345-4 0  9993"  # Hubble Space Telescope
# tle_line2_sat2 = "2 20580  28.4696 152.9981 0002944 343.0338  17.0332 15.09296073282714"

# Load satellite TLE data
tle_line1_TerraSAR = "1 31698U 07026A 23252.22345678 .00000123 00000+0 23456-4 0 9990"
tle_line2_TerraSAR = "2 31698 97.4433 125.6578 0001245 125.6324 234.5678 15.24567890123456"

tle_line1_TanDEMx = "1 36605U 10030A 23252.12345678 .00000145 00000+0 23456-5 0 9993"
tle_line2_TanDEMx = "2 36605 97.4440 125.1234 0001333 126.2345 233.4567 15.24678901234567"

# Create EarthSatellite objects
satellite1 = EarthSatellite(tle_line1_TerraSAR, tle_line2_TerraSAR, "ISS", load.timescale())
satellite2 = EarthSatellite(tle_line1_TanDEMx, tle_line2_TanDEMx, "Hubble Space Telescope", load.timescale())

# Define observer locations
target1 = Topos('40.7128 N', '74.0060 W')  # New York City
target2 = Topos('51.5074 N', '0.1278 W')   # London

# Load timescale and define the time range
ts = load.timescale()
start_time = ts.utc(2023, 9, 1, 0, 0, 0)
end_time = start_time + timedelta(hours=1)  # 1 hour window
time_range = ts.utc(start_time.utc_jpl()[0], start_time.utc_jpl()[1], start_time.utc_jpl()[2],
                    range(0, 3600, 10))  # Every 10 seconds

# Function to check visibility
def check_visibility(satellite, target, times):
    difference = satellite - target
    alt, az, distance = difference.at(times).altaz()
    visible_times = times[alt.degrees > 0]
    return visible_times

# Check visibility for Satellite 1
visible_times_sat1_target1 = check_visibility(satellite1, target1, time_range)
visible_times_sat1_target2 = check_visibility(satellite1, target2, time_range)

# Check visibility for Satellite 2
visible_times_sat2_target1 = check_visibility(satellite2, target1, time_range)
visible_times_sat2_target2 = check_visibility(satellite2, target2, time_range)

# Print visibility results
print("Satellite 1 (ISS) visibility from Target 1 (New York City):")
for t in visible_times_sat1_target1.utc_iso():
    print(t)

print("\nSatellite 1 (ISS) visibility from Target 2 (London):")
for t in visible_times_sat1_target2.utc_iso():
    print(t)

print("\nSatellite 2 (Hubble Space Telescope) visibility from Target 1 (New York City):")
for t in visible_times_sat2_target1.utc_iso():
    print(t)

print("\nSatellite 2 (Hubble Space Telescope) visibility from Target 2 (London):")
for t in visible_times_sat2_target2.utc_iso():
    print(t)
