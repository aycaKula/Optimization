from mip import Model, xsum, MINIMIZE, BINARY, CONTINUOUS
import math

num_satellites = 2
time_step = range(15)
num_time_step = len(time_step)

# Communication constraints parameters
# Uplinking speed
uplink_Rate = 64 # kbps

# Downlink data rate
downlink_Rate = 300 # Mbps

# Initial onboard memory for each satellite (in MB, for example)
initial_memory = [3000, 3000]  # Adjust based on satellite specifications

# Memory consumption per task (this is an example, adjust based on real data)
memory_consumption_per_task = [100, 200, 150, 120, 180]  # Memory usage for each task in MB

# Hardware communication limit
kappa_MO = 3

# Minimum communication time
TC_min = 1

# Communication bandwidth (MB per time slot, for example)
communication_bandwidth = 50  # Maximum data that can be transmitted per time slot

# Onboard memory decreases over time as data is transferred
M_S = [[10 for _ in range(num_time_step)] for _ in range(num_satellites)]

# Create a new model
model = Model(sense=MINIMIZE) # Model(sense=MINIMIZE, solver_name= GRB)

# Decision variables
# Communication end time for satellite i
y_E = [[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)]

# Communication start time for satellite i
y_S = [[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)]
mu_S_ij = [[[model.add_var(var_type=BINARY) for _ in range(num_time_step)] for _ in range(num_satellites)] for _ in
           range(num_satellites)]


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


