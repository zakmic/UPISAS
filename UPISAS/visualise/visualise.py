import pandas as pd
import matplotlib.pyplot as plt

# Load the combined CSV file
file_path = "combined_run_var_rate.csv"  # Update this if needed
data = pd.read_csv(file_path)

# Ensure the 'image' column is sorted for temporal progression analysis
data = data.sort_values(by="image").reset_index(drop=True)

# Clean the 'model' column: Convert non-string values to NaN
data["model"] = data["model"].astype(str).where(data["model"].isin(["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"]))

# Define the desired model order and ensure it's categorical
model_categories = ["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"]
data["model"] = pd.Categorical(data["model"], categories=model_categories, ordered=True)

# Drop rows with NaN in the 'model' column (optional, depending on your data)
data = data.dropna(subset=["model"])

# Plot 1: Model usage over time (image progression) with reversed y-axis order
plt.figure(figsize=(10, 6))
plt.plot(data["image"], data["model"], marker="o")
plt.title("Model Usage Over Time")
plt.xlabel("Image Number")
plt.ylabel("YOLO Model")
# plt.gca().invert_yaxis()  # Reverse the y-axis order so yolov5l is at the top
plt.grid()
plt.show()

# Plot 2: Comparison of var_rate, CPU utilization, and model usage
plt.figure(figsize=(10, 6))
plt.plot(data["image"], data["var_rate"], label="Var Rate", marker="o")
plt.plot(data["image"], data["cpu_utility"], label="CPU Utilization", marker="x")
plt.title("Var Rate and CPU Utilization Over Time")
plt.xlabel("Image Number")
plt.ylabel("Metric Value")
plt.legend()
plt.grid()
plt.show()

# Plot 3: CPU Utilization by YOLO Model
cpu_by_model = data.groupby("model")["cpu_utility"].mean()
cpu_by_model.plot(kind="bar", figsize=(8, 6))
plt.title("Average CPU Utilization by YOLO Model")
plt.xlabel("YOLO Model")
plt.ylabel("Average CPU Utilization")
plt.grid()
plt.show()

# Plot 4: Image processing time progression
plt.figure(figsize=(10, 6))
plt.plot(data["image"], data["image_processing_time"], label="Image Processing Time", marker="o")
plt.title("Image Processing Time Progression")
plt.xlabel("Image Number")
plt.ylabel("Processing Time (s)")
plt.grid()
plt.show()

# Plot 4: Image processing time progression
plt.figure(figsize=(10, 6))
plt.plot(data["image"], data["model_processing_time"], label="Image Processing Time", marker="o")
plt.title("Model Processing Time Progression")
plt.xlabel("Image Number")
plt.ylabel("Processing Time (s)")
plt.grid()
plt.show()

# # Select only numeric columns for correlation calculation
# numeric_data = data.select_dtypes(include=["number"])
# correlations = numeric_data.corr()
#
# # Display the correlation matrix
# print("Correlations between numeric metrics:")
# print(correlations)
#
# # Optional: Visualize the correlation matrix
# plt.figure(figsize=(10, 8))
# plt.matshow(correlations, fignum=1, cmap="coolwarm")
# plt.colorbar()
# plt.xticks(range(len(correlations.columns)), correlations.columns, rotation=45, ha="left")
# plt.yticks(range(len(correlations.columns)), correlations.columns)
# plt.title("Correlation Matrix of Numeric Metrics", pad=20)
# plt.show()
