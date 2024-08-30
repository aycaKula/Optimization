from mip import Model, xsum, BINARY, MINIMIZE
import numpy as np
import matplotlib.pyplot as plt

# Parameters
num_satellites = 2  # Two satellites
num_tasks = 5  # Example: 5 tasks

time_step = range(15)
num_time_step = len(time_step)  # Example: 10 time steps

# Satellite positions over time (example)
sat1_position = [2 * ts + 1 for ts in time_step]
sat2_position = [2 * ts + 2 for ts in time_step]

# Example positions of satellites (this could be more complex in a real scenario)
positions = {
    0: [1, 2],  # Satellite 1 position, Satellite 2 position at time slot 0
    1: [3, 4],
    2: [5, 6],
    3: [7, 8],
    4: [9, 10],
    5: [11, 12],
    6: [13, 14],
    7: [15, 16],
    8: [17, 18],
    9: [19, 20],
    10: [21, 22],
    11: [23, 24],
    12: [25, 26],
    13: [27, 28],
    14: [29, 30],
}

# Task requirements (simplified)
tasks = {
    0: {"start": 0, "end": 5, "processing_time": 2},  # Task 0
    1: {"start": 1, "end": 15, "processing_time": 1},  # Task 1
    2: {"start": 3, "end": 13, "processing_time": 2},  # Task 2
    3: {"start": 1, "end": 10, "processing_time": 1},  # Task 3
    4: {"start": 3, "end": 10, "processing_time": 2},  # Task 4
}

# Observation windows for each satellite (in seconds)
observation_windows = {
    0: {  # Observation windows for Satellite 1
        0: [(0, 5)],          # Task 0 can be observed from 0 to 5 seconds
        1: [(1, 7)],          # Task 1 can be observed from 1 to 7 seconds
        2: [(10, 15)],        # Task 2 can be observed from 10 to 15 seconds
        3: [(4, 9)],          # Task 3 can be observed from 4 to 9 seconds
        4: [(8, 12)],         # Task 4 can be observed from 8 to 12 seconds
    },
    1: {  # Observation windows for Satellite 2
        0: [(3, 8)],          # Task 0 can be observed from 3 to 8 seconds
        1: [(0, 4), (10, 15)],# Task 1 can be observed from 0 to 4 seconds and 10 to 15 seconds
        2: [(6, 10)],         # Task 2 can be observed from 6 to 10 seconds
        3: [(2, 7)],          # Task 3 can be observed from 2 to 7 seconds
        4: [(5, 9)],          # Task 4 can be observed from 5 to 9 seconds
    }
}

# Create a new model
model = Model(sense=MINIMIZE)

# Decision variables
x = [[[model.add_var(var_type=BINARY) for t in range(num_time_step)] for i in range(num_satellites)] for j in range(num_tasks)]

# Constraint: Each task must be assigned exactly once to one satellite during its processing time
for j in range(num_tasks):
    model += xsum(x[j][i][t] for i in range(num_satellites) for t in range(tasks[j]["start"], tasks[j]["end"])) == tasks[j]["processing_time"]

# Constraint: A task can only be assigned to a satellite if it's within the observation window
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            in_window = any(start <= t <= end for start, end in observation_windows[i][j])
            if not in_window:
                model += x[j][i][t] == 0

# Constraint: Non-overlapping task assignments for each satellite
for i in range(num_satellites):
    for t in range(num_time_step):
        model += xsum(x[j][i][t] for j in range(num_tasks)) <= 1

# Objective function: minimize the start time of tasks
model.objective = xsum(x[j][i][t] * t for j in range(num_tasks) for i in range(num_satellites) for t in range(num_time_step))

# Solve the problem
model.optimize()

decision_matrix = np.zeros((num_tasks, num_satellites, num_time_step), dtype=int)

# Output the results
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            if x[j][i][t].x >= 0.99:  # Checking if the variable is effectively 1
                decision_matrix[j][i][t:t + tasks[j]["processing_time"]] = 1
                print(f"Task {j} is assigned to satellite {i} at time step {t}")

# Visualization
fig, ax = plt.subplots(num_tasks, num_satellites, figsize=(15, 15))
for i in range(num_tasks):
    for j in range(num_satellites):
        ax[i, j].imshow(decision_matrix[i, j].reshape(1, -1), cmap='gray_r', aspect='auto')
        ax[i, j].set_xticks(range(num_time_step))
        ax[i, j].set_yticks([])
        ax[i, j].set_title(f'Task {i}, Satellite {j}')

fig.suptitle('Optimized Decision Variables Matrix (x[i][j][k])')
plt.show()
