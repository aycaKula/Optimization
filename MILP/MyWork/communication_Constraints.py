from mip import Model, xsum, MINIMIZE, BINARY, CONTINUOUS
import math

num_satellites = 2
time_step = range(15)
num_time_step = len(time_step)

# Dynamic equations for a satellite in circular orbit
G = 6.67430e-11  # Gravitational constant in m^3 kg^(-1) s^(-2)
M = 5.972e24  # Mass of the Earth in kg
mu = G * M
R_e = 6371 # km
R_m = R_e * 1000  # Radius of the Earth in meters
h = 100 # km

# Assume it is circular
r = R_e + h
r_m = r*1000

# Orbital period (T)
T = 2 * math.pi * math.sqrt(r**3 / mu)  # Orbital period in seconds

# Mean motion (n)
n = 2 * math.pi / T  # Mean motion in rad/s


# Function to convert lat/long to Cartesian coordinates
def lat_long_to_cartesian(lat, lon):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = R_m * math.cos(lat_rad) * math.cos(lon_rad)
    y = R_m * math.cos(lat_rad) * math.sin(lon_rad)
    z = R_m * math.sin(lat_rad)
    return x, y, z


# Function to calculate satellite's position at time t
def satellite_position(t, n, r):
    x = r * math.cos(n * t)
    y = r * math.sin(n * t)
    z = 0  # Assuming equatorial orbit
    return x, y, z


# Function to check if target is visible
def is_visible(sat_pos, target_pos, threshold=1000000):  # 1000 km threshold
    distance = math.sqrt((sat_pos[0] - target_pos[0])**2 + (sat_pos[1] - target_pos[1])**2 + (sat_pos[2] - target_pos[2])**2)
    return distance <= threshold


# Example targets (latitude, longitude) in degrees
targets = [
    (0, 0),      # Target 1 (Equator)
    (45, 45),    # Target 2 (Mid-latitude)
    (60, -30),   # Target 3 (High-latitude)
    (-30, 120)   # Target 4 (Southern Hemisphere)
]

# Convert targets to Cartesian coordinates
target_positions = [lat_long_to_cartesian(lat, lon) for lat, lon in targets]

# Simulate orbits and check visibility
t_values = range(0, int(T), 100)  # Simulate for one orbital period with 100s intervals

satellites = ["Satellite 1", "Satellite 2"]
satellite_positions = []

# Simulate positions for two satellites
for i in range(2):
    satellite_positions.append([satellite_position(t, n + i * 0.001, r_m) for t in t_values])

# Check which targets are visible for each satellite
visibility_results = {sat: {t: [] for t in t_values} for sat in satellites}

for i, sat_pos_list in enumerate(satellite_positions):
    for t_idx, sat_pos in enumerate(sat_pos_list):
        t = t_values[t_idx]
        for j, target_pos in enumerate(target_positions):
            if is_visible(sat_pos, target_pos):
                visibility_results[satellites[i]][t].append(f"Target {j + 1}")

# Output the results
for sat, visibility in visibility_results.items():
    print(f"{sat} visibility:")
    for t, targets_visible in visibility.items():
        print(f"  Time {t} seconds: {', '.join(targets_visible) if targets_visible else 'No targets visible'}")


# Initial onboard memory for each satellite (in MB, for example)
initial_memory = [3000, 3000]  # Adjust based on satellite specifications

# Onboard memory decreases over time as data is transferred
M_S = [[10 for _ in range(num_time_step)] for _ in range(num_satellites)]

# Communication constraints parameters
# Comm_data_rate

# Uplinking speed
# uplink_spd = 64
comm_S = 64 # I think that the communication rate and the uplink spd is related paraemeters??????

# Memory consumption per task (this is an example, adjust based on real data)
memory_consumption_per_task = [100, 200, 150, 120, 180]  # Memory usage for each task in MB

kappa_MO = 3  # Hardware communication limit
TC_min = 1  # Minimum communication time

# Communication bandwidth (MB per time slot, for example)
communication_bandwidth = 50  # Maximum data that can be transmitted per time slot

# Create a new model
model = Model(sense=MINIMIZE) # Model(sense=MINIMIZE, solver_name= GRB)

# Decision variables
# Communication end time for satellite i
y_E = [[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)]

# Communication start time for satellite i
y_S = [[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)]
mu_S_ij = [[[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)] for _ in
           range(num_satellites)]

"""
# Observation window constraints
for i in range(num_satellites):
    for t in range(num_time_step):
        model += obs_start[i][t] >= observation_windows[i][t][0]  # Start within observation window
        model += obs_end[i][t] <= observation_windows[i][t][1]    # End within observation window

# Communication window constraints
for i in range(num_satellites):
    for t in range(num_time_step):
        model += comm_start[i][t] >= communication_windows[i][t][0]  # Start time within communication window
        model += comm_end[i][t] <= communication_windows[i][t][1]    # End time within communication window
"""
# Communication constraints
for i in range(num_satellites):
    memory_used = initial_memory[i]
    for t in range(num_time_step):
        data_collected = xsum(memory_consumption_per_task[j] * y[j][t] for j in range(num_tasks))
        data_transmitted = communication_bandwidth * t
        memory_used += data_collected - data_transmitted

        # Ensure that the memory used does not exceed the initial memory
        model += memory_used <= initial_memory[i]

# Constraint 1: Communication start time shall always be ahead or at least equal to the end time
for i in range(num_satellites):
    for k in range(num_time_step):
        model += y_E[i][k] >= y_S[i][k]

# Constraint 2: Amount of data transferred in a communication window in one orbit shall be less than the raw data it contains.
# Amount of data transferred in the orbit shall be less than the raw data that onboard memory has at the start of this circle,
# plus the amount of data that it has gathered in this orbit.
for i in range(num_satellites):
    for k in range(num_time_step):
        model += (y_E[i][k] - y_S[i][k]) * comm_S[i] <= initial_memory[i] - M_S[i][k] + (y_E[i][k] - y_S[i][k]) / obs_S[
            i]

# Constraint 3: Avoid communication jamming
for k in range(num_time_step):
    model += xsum(mu_S_ij[i][j][k] for i in range(num_satellites) for j in range(num_satellites)) <= kappa_MO

# Constraint 4: Minimum communication time
for i in range(num_satellites):
    for k in range(num_time_step):
        model += y_E[i][k] - y_S[i][k] >= TC_min