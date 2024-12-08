import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load and clean data
file_path = "combined_run_var_rate.csv"  # Replace with your actual file path
data = pd.read_csv(file_path)

# Define model colors
model_colors = {
    "yolov5n": "#ffcccc",  # light red
    "yolov5s": "#ccffcc",  # light green
    "yolov5m": "#ccccff",  # light blue
    "yolov5l": "#ffffcc",  # light yellow
    "yolov5x": "#ffccff",  # light magenta
}

# Drop duplicates based on 'image' to ensure unique shading
data_unique = data.drop_duplicates(subset=['image'], keep='first')

### PLOT 1: Input Rate over Time with Model Usage Shading (No Whitespace)
plt.figure(figsize=(14, 8))
ax = plt.gca()

# Plot input rate
ax.plot(data_unique['image'], data_unique['input_rate'], color='black', label='Input Rate')

# Shade model usage
for i in range(len(data_unique) - 1):
    start_image = data_unique['image'].iloc[i]
    end_image = data_unique['image'].iloc[i + 1]
    model = data_unique['model'].iloc[i]
    color = model_colors.get(model, '#ffffff')  # Default to white if model not defined
    ax.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

# Add legend
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]
input_rate_line = plt.Line2D([], [], color='black', label='Input Rate')
plt.legend(handles=model_patches + [input_rate_line], loc='upper right')

# Label axes and title
plt.xlabel('Image Number')
plt.ylabel('Input Rate (requests per second)')
plt.title('Input Rate over Time with Model Usage Shading (No Whitespace)')
plt.grid()
plt.show()

### PLOT 2: Model Processing Time with Input Rate and Model Usage Shading
fig, ax1 = plt.subplots(figsize=(14, 8))

# Plot model processing time
ax1.plot(data_unique['image'], data_unique['model_processing_time'], label='Model Processing Time', color='blue')
ax1.set_xlabel('Image Number')
ax1.set_ylabel('Processing Time (s)')
ax1.legend(loc='upper left')
ax1.grid()

# Twin axis for input_rate
ax2 = ax1.twinx()
ax2.plot(data_unique['image'], data_unique['input_rate'], label='Input Rate', color='red', linestyle='--')
ax2.set_ylabel('Input Rate (requests per second)')
ax2.legend(loc='upper right')

# Add model usage shading
for i in range(len(data_unique) - 1):
    start_image = data_unique['image'].iloc[i]
    end_image = data_unique['image'].iloc[i + 1]
    model = data_unique['model'].iloc[i]
    color = model_colors.get(model, '#ffffff')
    ax1.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

# Add legend for model shading
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]

# Collect handles and labels from both axes
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

# Combine all handles and labels, including model patches
handles = handles1 + handles2 + model_patches
labels = labels1 + labels2 + [model for model in model_colors.keys()]

# Pass valid handles and labels to plt.legend
plt.legend(handles, labels, loc='upper center', ncol=3)

plt.title('Model Processing Time with Input Rate and Model Usage Shading')
plt.show()

### PLOT 3: Utility over Image Number with Input Rate and Model Usage Shading
fig, ax1 = plt.subplots(figsize=(14, 8))

# Plot utility
ax1.plot(data_unique['image'], data_unique['utility'], label='Utility', color='green')
ax1.set_xlabel('Image Number')
ax1.set_ylabel('Utility')
ax1.legend(loc='upper left')
ax1.grid()

# Twin axis for input_rate
ax2 = ax1.twinx()
ax2.plot(data_unique['image'], data_unique['input_rate'], label='Input Rate', color='red', linestyle='--')
ax2.set_ylabel('Input Rate (requests per second)')
ax2.legend(loc='upper right')

# Add model usage shading
for i in range(len(data_unique) - 1):
    start_image = data_unique['image'].iloc[i]
    end_image = data_unique['image'].iloc[i + 1]
    model = data_unique['model'].iloc[i]
    color = model_colors.get(model, '#ffffff')
    ax1.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

# Add legend for model shading
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2 + model_patches
labels = labels1 + labels2 + [model for model in model_colors.keys()]
plt.legend(handles, labels, loc='upper center', ncol=3)

plt.title('Utility over Image Number with Input Rate and Model Usage Shading')
plt.show()

### PLOT 4: Average CPU Utilization by YOLO Model
cpu_by_model = data.groupby("model")["cpu_utility"].mean()
cpu_by_model = cpu_by_model.reindex(model_colors.keys())  # Ensure correct order
cpu_by_model.plot(kind="bar", figsize=(10, 6), color=list(model_colors.values()))
plt.title("Average CPU Utilization by YOLO Model")
plt.xlabel("YOLO Model")
plt.ylabel("Average CPU Utilization (%)")
plt.grid()
plt.show()
