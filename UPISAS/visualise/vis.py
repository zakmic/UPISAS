import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # For legend patches

# Load the combined CSV file
file_path = "combined_run_var_rate.csv"  # Update this if needed
data = pd.read_csv(file_path)

# Ensure the 'image' column is sorted for temporal progression analysis
data = data.sort_values(by="image").reset_index(drop=True)

# Clean the 'model' column: Convert non-string values to NaN
data["model"] = data["model"].astype(str)
valid_models = ["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"]
data["model"] = data["model"].where(data["model"].isin(valid_models))

# Define the desired model order and ensure it's categorical
model_categories = ["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"]
data["model"] = pd.Categorical(data["model"], categories=model_categories, ordered=True)

# Drop rows with NaN in the 'model' column
data = data.dropna(subset=["model"])

# Assign numerical weights to models for plotting (if needed)
model_weights = {"yolov5n": 1, "yolov5s": 2, "yolov5m": 3, "yolov5l": 4, "yolov5x": 5}
data["model_weight"] = data["model"].map(model_weights)

# Assign colors to models for shading
model_colors = {
    "yolov5n": "#ffcccc",  # light red
    "yolov5s": "#ccffcc",  # light green
    "yolov5m": "#ccccff",  # light blue
    "yolov5l": "#ffffcc",  # light yellow
    "yolov5x": "#ffccff",  # light magenta
}

# Plot 1: Input Rate over Image Number with Model Shading
plt.figure(figsize=(12, 6))

ax = plt.gca()

# Create model segments by identifying when the model changes
data['model_change'] = (data['model'] != data['model'].shift()).cumsum()

for key, grp in data.groupby('model_change'):
    model = grp['model'].iloc[0]
    color = model_colors.get(model, '#ffffff')  # default to white if model not found
    start_image = grp['image'].iloc[0]
    end_image = grp['image'].iloc[-1]
    ax.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

ax.plot(data['image'], data['input_rate'], color='black', label='Input Rate')

# Create custom legend for models and input rate
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]
input_rate_line = plt.Line2D([], [], color='black', label='Input Rate')
plt.legend(handles=model_patches + [input_rate_line], loc='upper right')

plt.xlabel('Image Number')
plt.ylabel('Input Rate (requests per second)')
plt.title('Input Rate over Time with Model Usage Shading')
plt.grid()
plt.show()

# Plot 2a: Model Processing Time over Image Number with Input Rate and Model Shading
plt.figure(figsize=(12, 6))

ax1 = plt.gca()

# Shade background based on model used
for key, grp in data.groupby('model_change'):
    model = grp['model'].iloc[0]
    color = model_colors.get(model, '#ffffff')
    start_image = grp['image'].iloc[0]
    end_image = grp['image'].iloc[-1]
    ax1.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

# Plot model processing time
ax1.plot(data['image'], data['model_processing_time'], label='Model Processing Time', color='blue')
ax1.set_xlabel('Image Number')
ax1.set_ylabel('Processing Time (s)')
ax1.legend(loc='upper left')
ax1.grid()

# Create a twin axis for input_rate
ax2 = ax1.twinx()
ax2.plot(data['image'], data['input_rate'], label='Input Rate', color='red', linestyle='--')
ax2.set_ylabel('Input Rate (requests per second)')
ax2.legend(loc='upper right')

# Add legend for model shading
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]
handles, labels = [], []
for h, l in zip(*ax1.get_legend_handles_labels()):
    handles.append(h)
    labels.append(l)
for h, l in zip(*ax2.get_legend_handles_labels()):
    handles.append(h)
    labels.append(l)
handles.extend(model_patches)
labels.extend([model for model in model_colors.keys()])
plt.legend(handles, labels, loc='upper center', ncol=3)

plt.title('Model Processing Time with Input Rate and Model Usage Shading')
plt.show()

# Plot 2b: Image Processing Time over Image Number with Input Rate and Model Shading
plt.figure(figsize=(12, 6))

ax1 = plt.gca()

# Shade background based on model used
for key, grp in data.groupby('model_change'):
    model = grp['model'].iloc[0]
    color = model_colors.get(model, '#ffffff')
    start_image = grp['image'].iloc[0]
    end_image = grp['image'].iloc[-1]
    ax1.axvspan(start_image, end_image, facecolor=color, alpha=0.3)

# Plot image processing time
ax1.plot(data['image'], data['image_processing_time'], label='Image Processing Time', color='green')
ax1.set_xlabel('Image Number')
ax1.set_ylabel('Processing Time (s)')
ax1.legend(loc='upper left')
ax1.grid()

# Create a twin axis for input_rate
ax2 = ax1.twinx()
ax2.plot(data['image'], data['input_rate'], label='Input Rate', color='red', linestyle='--')
ax2.set_ylabel('Input Rate (requests per second)')
ax2.legend(loc='upper right')

# Add legend for model shading
model_patches = [mpatches.Patch(color=color, label=model) for model, color in model_colors.items()]
handles, labels = [], []
for h, l in zip(*ax1.get_legend_handles_labels()):
    handles.append(h)
    labels.append(l)
for h, l in zip(*ax2.get_legend_handles_labels()):
    handles.append(h)
    labels.append(l)
handles.extend(model_patches)
labels.extend([model for model in model_colors.keys()])
plt.legend(handles, labels, loc='upper center', ncol=3)

plt.title('Image Processing Time with Input Rate and Model Usage Shading')
plt.show()

# Plot 3: CPU Utilization by YOLO Model
cpu_by_model = data.groupby("model")["cpu_utility"].mean()
cpu_by_model = cpu_by_model.reindex(model_categories)  # Ensure correct order
cpu_by_model.plot(kind="bar", figsize=(8, 6))
plt.title("Average CPU Utilization by YOLO Model")
plt.xlabel("YOLO Model")
plt.ylabel("Average CPU Utilization")
plt.grid()
plt.show()