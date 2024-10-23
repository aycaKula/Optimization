import matplotlib.pyplot as plt


# Assuming decision_matrix shape is (num_tasks, num_satellites, num_time_step)
# and is already computed from your model optimization

fig, ax = plt.subplots(figsize=(12, 8))

colors = ['blue', 'red']  # Colors for the satellites. Extend this list if more satellites.

# Iterate through each task and satellite to plot
for task in range(num_tasks):
    # Draw the overall task duration from start to end
    task_start = tasks[task]["start"]
    task_end = tasks[task]["end"]
    ax.plot([task_start, task_end], [task + 0.5, task + 0.5], color='gray', linewidth=25, alpha=0.3, solid_capstyle='butt', label='Task Duration' if task == 0 else "")

    # This dictionary will collect the total processing time per task
    total_processing_time_per_task = {sat: 0 for sat in range(num_satellites)}

    for satellite in range(num_satellites):
        time_step = task_start
        while time_step <= task_end:
            if decision_matrix[task][satellite][time_step] == 1:
                # Find the stretch of continuous active time steps
                start = time_step
                while time_step <= task_end and decision_matrix[task][satellite][time_step] == 1:
                    time_step += 1
                end = time_step - 1
                total_processing_time_per_task[satellite] += (end - start + 1)
                ax.plot([start, end + 1], [task + 0.5, task + 0.5], solid_capstyle='butt',
                        linewidth=20, color=colors[satellite], label=f'Satellite {satellite}' if task == 0 and satellite == 0 else "")
            else:
                time_step += 1

    # Highlight the processing time separately if it fits within the task duration
    processing_start = task_start  # This assumes the processing starts at the task start, adjust if different
    processing_time = tasks[task]["processing_time"]
    if sum(total_processing_time_per_task.values()) == processing_time:
        processing_end = processing_start + processing_time
        ax.plot([processing_start, processing_end], [task + 0.5, task + 0.5], color='black', linewidth=15, label='Processing Time' if task == 0 else "")

# Setting the y-ticks to be at the center of the tasks
ax.set_yticks([t + 0.5 for t in range(num_tasks)])
ax.set_yticklabels([f'Task {t}' for t in range(num_tasks)])

ax.set_xlabel('Time Step')
ax.set_ylabel('Tasks')
ax.set_title('Task Assignments and Timelines by Satellite')
ax.set_xlim(0, num_time_step)

# Create custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='gray', lw=4, label='Task Duration', alpha=0.3),
    Line2D([0], [0], color='black', lw=4, label='Processing Time'),
] + [Line2D([0], [0], color=colors[i], lw=4, label=f'Satellite {i}') for i in range(num_satellites)]
ax.legend(handles=legend_elements)

ax.grid(True)
plt.show()
