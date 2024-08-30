from mip import Model, xsum, BINARY, MINIMIZE
import matplotlib.pyplot as plt
import numpy as np

# Parameters
num_satellites = 2  # Two satellites
num_tasks = 5  # Example: 5 tasks

time_step = range(9)
num_time_step = len(time_step)  # Example: 15 time steps

# Data for satellite positions (Moving at same speed)
sat1_position = [2 * ts + 1 for ts in time_step]  # Satellite 1 moving uniformly
sat2_position = [2 * ts + 2 for ts in time_step]  # Satellite 2 moving uniformly

positions = {time_step: [sat1_position, sat2_position] for time_step, sat1_position, sat2_position in zip(time_step, sat1_position, sat2_position)}

"""
# Example positions of satellites (this could be more complex in a real scenario)
positions = {
    0: [1, 2],  # Satellite 1 position, Satellite 2 position at time slot 0
    1: [3, 4],  # Satellite 1 position, Satellite 2 position at time slot 1
    2: [5, 6],  # Continue this pattern for all time slots
    3: [7, 8],
    4: [9, 10],
    5: [11, 12],
    6: [13, 14],
    7: [15, 16],
    8: [17, 18],
    9: [19, 20],
}
"""

# Orbit and Satellite Positions Over Time
plt.figure(figsize=(10, 6))
plt.plot(time_step, sat1_position, marker='o', label='Satellite 1')
plt.plot(time_step, sat2_position, marker='s', label='Satellite 2')
plt.xlabel('Time Slot')
plt.ylabel('Position')
plt.title('Satellite Positions Over Time')
plt.legend()
plt.grid(True)
plt.show()


# Create a new model
model = Model(sense=MINIMIZE) # Model(sense=MINIMIZE, solver_name= GRB)

# Add Decision variables
x = [[[model.add_var(var_type=BINARY) for t in range(num_time_step)] for i in range(num_satellites)] for j in range(num_tasks)]
y = [[model.add_var(var_type=BINARY) for t in range(num_time_step)] for j in range(num_tasks)]


# Task requirements (simplified)
# Start and end time indicates that the task should be finished within this time interval
tasks = {
    0: {"start": 0, "end": 8, "processing_time": 2},  # Task 0
    1: {"start": 0, "end": 8, "processing_time": 1},  # Task 1
    2: {"start": 0, "end": 8, "processing_time": 2},  # Task 2
    3: {"start": 0, "end": 8, "processing_time": 1},  # Task 3
    4: {"start": 0, "end": 8, "processing_time": 2},  # Task 4
}


# Observation windows for each satellite (in seconds)
observation_windows = {
    0: {  # Observation windows for Satellite 1
        0: [(0, 3)],          # Task 0 can be observed from 0 to 5 seconds
        1: [(1, 4)],          # Task 1 can be observed from 1 to 7 seconds
        2: [(1, 5)],        # Task 2 can be observed from 10 to 15 seconds
        3: [(2, 5)],          # Task 3 can be observed from 4 to 9 seconds
        4: [(2, 6)],         # Task 4 can be observed from 8 to 12 seconds
    },
    1: {  # Observation windows for Satellite 2
        0: [(1, 7)],          # Task 0 can be observed from 3 to 8 seconds
        1: [(1, 4), (5, 7)],# Task 1 can be observed from 0 to 4 seconds and 10 to 15 seconds
        2: [(2, 5)],         # Task 2 can be observed from 6 to 10 seconds
        3: [(6, 7)],          # Task 3 can be observed from 2 to 7 seconds
        4: [(2, 4)],          # Task 4 can be observed from 5 to 9 seconds
    }
}

# Tasks Timeline
plt.figure(figsize=(10, 6))
for task, details in tasks.items():
    plt.plot([details["start"], details["end"]], [task, task], marker='o', label=f'Task {task}')
    plt.plot([details["start"], details["start"] + details["processing_time"]], [task, task], marker='|', linestyle='-', linewidth=5)

plt.xlabel('Time Slot')
plt.ylabel('Task')
plt.title('Tasks Timeline')
plt.legend()
plt.grid(True)
plt.show()

# Constraints
# Constraint 1: Each task is assigned exactly once within their start-end time
"""
THIS IS ERASED BECAUSE THE SIGN MUST BE BIGGER AND EQUAL TO
for j in range(num_tasks):
    model += xsum(x[j][i][t] for i in range(num_satellites) for t in range(num_time_step)) == 1
"""
#for j in range(num_tasks):
    #for i in range(num_satellites):
    # model += xsum(x[j][i][t] for i in range(num_satellites) for t in range(num_time_step)) == 1
    #  model += xsum(x[j][i][t] for i in range(num_satellites) for t in range(tasks[j]["start"], tasks[j]["end"])) >= 1
    # model += xsum(x[j][i][t] for i in range(num_satellites) for t in range(tasks[j]["start"], tasks[j]["end"])) == tasks[j]["processing_time"]
    #   model += xsum(x[j][i][t] for t in range(tasks[j]["start"], tasks[j]["end"])) == y[j][i]


for j in range(num_tasks):
    for t in range(tasks[j]["start"], tasks[j]["end"]):
        model += xsum(x[j][i][t] for i in range(num_satellites)) == y[j][t]


for j in range(num_tasks):
    model += xsum(y[j][t] for t in range(tasks[j]["start"], tasks[j]["end"])) == tasks[j]["processing_time"]


# Constraint 2: Tasks must be assigned within their allowed time window
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            if t < tasks[j]["start"] or t > tasks[j]["end"]:
                model += x[j][i][t] == 0 # The task must assigned between the task's start and end time


"""
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            if tasks[j]["start"] + tasks[j]["processing_time"] <= tasks[j]["end"]:
                model += x[j][i][t] == 0
"""

# Constraint 3: Non-overlapping task assignments for each satellite

for i in range(num_satellites):
    for j in range(num_tasks):
        for t in range(tasks[j]["start"], tasks[j]["end"]): # since I am adding processing time in the line below
            for t_prime in range(t, t + tasks[j]["processing_time"]):
                for j_prime in range(num_tasks):
                    if j_prime != j: # For different tasks
                        model += x[j][i][t] + x[j_prime][i][t_prime] <= 1

"""
for i in range(num_satellites):
    for j in range(num_tasks):
        for t in range(tasks[j]["start"], tasks[j]["end"]): # since I am adding processing time in the line below
                for j_prime in range(num_tasks):
                    if j_prime != j: # For different tasks
                        model += x[j][i][t] + x[j_prime][i][t] <= 1
"""

# Observation constraints
# Constraint 4 : Assign task j to satellite i only if it lies within the observation window
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            in_window = any(start_time <= t <= end_time for start_time, end_time in observation_windows[i][j])
            if not in_window:
                model += x[j][i][t] == 0


# Objective function: minimize total processing time (example)
#model.objective = xsum(x[j][i][t] * tasks[j]["processing_time"] for j in range(num_tasks) for i in range(num_satellites) for t in range(num_time_step))
model.objective = xsum(x[j][i][t] * t for j in range(num_tasks) for i in range(num_satellites) for t in range(num_time_step))


# Solve the problem
model.optimize()

# Debugging: Print the values of the decision variables
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            if x[j][i][t].x >= 0.99:  # Check if the variable is effectively 1
                print(f"x[{j}][{i}][{t}] = 1")  # Task j is assigned to satellite i at time t

decision_matrix = np.zeros((num_tasks, num_satellites, num_time_step), dtype=int)
# Output the results
for j in range(num_tasks):
    for i in range(num_satellites):
        for t in range(num_time_step):
            if x[j][i][t].x >= 0.99:  # Checking if the variable is effectively 1
                # decision_matrix[j][i][t] = 1
                decision_matrix[j][i][t:t + tasks[j]["processing_time"]] = 1
                print(f"Task {j} is assigned to satellite {i} at time step {t}")


fig, ax = plt.subplots(num_tasks, num_satellites, figsize=(15, 15))
for i in range(num_tasks):
    for j in range(num_satellites):
        ax[i, j].imshow(decision_matrix[i, j].reshape(1, -1), cmap='gray_r', aspect='auto')
        ax[i, j].set_xticks(range(num_time_step))
        ax[i, j].set_yticks([])
        ax[i, j].set_title(f'Task {i}, Satellite {j}')

fig.suptitle('Optimized Decision Variables Matrix (x[i][j][k])')
plt.show()

