import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
import time

start_time = time.time()

# Parameters
num_satellites = 2  # Two satellites
num_tasks = 5
num_time_step = 7  # Number of time steps
num_channels = 3  # Number of communication channels

# Task requirements (simplified)
tasks = {
    0: {"start": 1, "end": 7, "processing_time": 2},
    1: {"start": 1, "end": 4, "processing_time": 1},
    2: {"start": 2, "end": 5, "processing_time": 1},
    3: {"start": 2, "end": 4, "processing_time": 1},
    4: {"start": 3, "end": 6, "processing_time": 2},
}

# Observation windows for each satellite (in seconds)
observation_windows = {
    0: {  # Observation windows for Satellite 1
        0: [(0, 3)],
        1: [(1, 4)],
        2: [(1, 5)],
        3: [(2, 5)],
        4: [(2, 6)],
    },
    1: {  # Observation windows for Satellite 2
        0: [(1, 7)],
        1: [(1, 4), (5, 7)],
        2: [(2, 5)],
        3: [(6, 7)],
        4: [(2, 4)],
    }
}

# Battery parameters
battery_capacity = [1000, 1000]  # Max battery capacity
initial_battery = [500, 500]  # Initial battery level
energy_consumption_per_task = [50, 100, 75, 60, 80]  # Energy consumed per task
charging_rate = [20, 20]  # Charging rate

# Communication parameters
initial_memory = [3000, 3000]  # Initial onboard memory
comm_S = 64  # Uplink speed and communication rate
memory_consumption_per_task = [100, 200, 150, 120, 180]  # Memory usage per task
kappa_MO = 3  # Hardware communication limit (jamming limit)
TC_min = 1  # Minimum communication time
communication_bandwidth = 50  # Maximum data transmission rate per time slot

# Boolean array to indicate if satellite is in sunlight
in_sunlight = [
    [1, 1, 1, 1, 0, 0, 0],  # Satellite 1
    [0, 0, 1, 1, 1, 0, 0]  # Satellite 2
]

# Decision variables
x = [[[cp.Variable(boolean=True) for t in range(num_time_step)] for i in range(num_satellites)] for j in
     range(num_tasks)]
y = [[cp.Variable(boolean=True) for t in range(num_time_step)] for j in range(num_tasks)]
battery_level = [[cp.Variable() for t in range(num_time_step)] for i in range(num_satellites)]
memory_used = [[cp.Variable() for t in range(num_time_step)] for i in range(num_satellites)]
y_S = [[cp.Variable(boolean=True) for _ in range(num_time_step)] for _ in range(num_satellites)]  # Comm start time
y_E = [[cp.Variable(boolean=True) for _ in range(num_time_step)] for _ in range(num_satellites)]  # Comm end time
mu_itc = [[[cp.Variable(boolean=True) for _ in range(num_channels)] for _ in range(num_time_step)] for _ in
          range(num_satellites)]  # Communication channel usage


# --------- Defining Constraint Functions ---------

def task_assignment_constraints(x, y, tasks, num_time_step):
    constraints = []
    for j in range(num_tasks):
        for t in range(tasks[j]["start"], tasks[j]["end"] + 1):
            constraints.append(cp.sum([x[j][i][t] for i in range(num_satellites)]) == y[j][t])
        constraints.append(
            cp.sum([y[j][t] for t in range(tasks[j]["start"], tasks[j]["end"] + 1)]) == tasks[j]["processing_time"])
    return constraints


def time_window_constraints(x, tasks, num_time_step):
    constraints = []
    for j in range(num_tasks):
        for i in range(num_satellites):
            for t in range(num_time_step):
                if t < tasks[j]["start"] or t > tasks[j]["end"]:
                    constraints.append(x[j][i][t] == 0)
    return constraints


def non_overlapping_constraints(x, tasks, num_satellites, num_time_step):
    constraints = []
    for i in range(num_satellites):
        for j in range(num_tasks):
            for t in range(tasks[j]["start"], tasks[j]["end"] + 1):
                for t_prime in range(t, min(t + tasks[j]["processing_time"], num_time_step)):
                    for j_prime in range(num_tasks):
                        if j_prime != j:
                            constraints.append(x[j][i][t] + x[j_prime][i][t_prime] <= 1)
    return constraints


def observation_window_constraints(x, observation_windows, num_time_step):
    constraints = []
    for j in range(num_tasks):
        for i in range(num_satellites):
            for t in range(num_time_step):
                in_window = any(start_time <= t <= end_time for start_time, end_time in observation_windows[i][j])
                if not in_window:
                    constraints.append(x[j][i][t] == 0)
    return constraints


# Battery Constraints
def battery_constraints(battery_level, x, in_sunlight, initial_battery, battery_capacity, energy_consumption_per_task,
                        charging_rate):
    constraints = []
    for i in range(num_satellites):
        constraints.append(battery_level[i][0] == initial_battery[i])  # Initial battery level
        for t in range(1, num_time_step):
            energy_consumed = cp.sum([energy_consumption_per_task[j] * x[j][i][t] for j in range(num_tasks)])
            energy_recharged = charging_rate[i] * in_sunlight[i][t]
            # Update battery level based on energy consumption and recharging
            constraints.append(battery_level[i][t] == battery_level[i][t - 1] + energy_recharged - energy_consumed)
            # Battery limits
            constraints.append(battery_level[i][t] >= 0)
            constraints.append(battery_level[i][t] <= battery_capacity[i])
    return constraints


# Communication Constraints
def communication_constraints(memory_used, y_S, y_E, mu_itc, initial_memory, memory_consumption_per_task,
                              communication_bandwidth, comm_S, kappa_MO, TC_min, num_channels):
    constraints = []

    # Memory update constraint
    for i in range(num_satellites):
        constraints.append(memory_used[i][0] == initial_memory[i])
        for t in range(1, num_time_step):
            data_collected = cp.sum([memory_consumption_per_task[j] * y[j][t] for j in range(num_tasks)])
            data_transmitted = communication_bandwidth * (y_E[i][t] - y_S[i][t])
            constraints.append(memory_used[i][t] == memory_used[i][t - 1] + data_collected - data_transmitted)
            constraints.append(memory_used[i][t] >= 0)
            constraints.append(memory_used[i][t] <= initial_memory[i])

    # Communication start must be before or equal to end time
    for i in range(num_satellites):
        for t in range(num_time_step):
            constraints.append(y_E[i][t] >= y_S[i][t])

    # Corrected Communication jamming constraint
    # Ensure that no more than kappa_MO satellites are using the same communication channel at time t
    for t in range(num_time_step):
        for c in range(num_channels):
            constraints.append(cp.sum([mu_itc[i][t][c] for i in range(num_satellites)]) <= kappa_MO)

    # Minimum communication time constraint
    for i in range(num_satellites):
        for t in range(num_time_step):
            constraints.append(y_E[i][t] - y_S[i][t] >= TC_min)

    return constraints


# --------- Build the optimization problem ---------

# Initialize constraints
constraints = []
constraints += task_assignment_constraints(x, y, tasks, num_time_step)
constraints += time_window_constraints(x, tasks, num_time_step)
constraints += non_overlapping_constraints(x, tasks, num_satellites, num_time_step)
constraints += observation_window_constraints(x, observation_windows, num_time_step)
constraints += battery_constraints(battery_level, x, in_sunlight, initial_battery, battery_capacity,
                                   energy_consumption_per_task, charging_rate)
constraints += communication_constraints(memory_used, y_S, y_E, mu_itc, initial_memory, memory_consumption_per_task,
                                         communication_bandwidth, comm_S, kappa_MO, TC_min, num_channels)

# Objective function: Minimize total time (example)
objective = cp.Minimize(
    cp.sum([x[j][i][t] * t for j in range(num_tasks) for i in range(num_satellites) for t in range(num_time_step)]))

# Define the problem
problem = cp.Problem(objective, constraints)

# Solve the problem
problem.solve()

print(f"Problem status: {problem.status}")
