import pandas as pd
import matplotlib.pyplot as plt

# Load the combined CSV
file_path = "combined_run_var_rate.csv"  # Update the path if needed
data = pd.read_csv(file_path)

# Ensure data is sorted by image
data = data.sort_values(by="image").reset_index(drop=True)

# Assign numerical weights to models
model_weights = {"yolov5n": 1, "yolov5s": 2, "yolov5m": 3, "yolov5l": 4, "yolov5x": 5}
data["model_weight"] = data["model"].map(model_weights)

# Plot 1: Model usage over time with var_rate
plt.figure(figsize=(12, 6))
plt.plot(data["image"], data["model"], marker="o", label="Model")
plt.scatter(data["image"], data["var_rate"], color="red", label="Var Rate", alpha=0.6)
plt.title("Model Usage Over Time with Var Rate Indication")
plt.xlabel("Image Number")
plt.ylabel("YOLO Model")
plt.gca().invert_yaxis()  # Largest model appears at the top
plt.legend()
plt.grid()
plt.show()

# Plot 2: Compare model_processing_time and image_processing_time to the model
plt.figure(figsize=(12, 6))
plt.scatter(data["model"], data["model_processing_time"], label="Model Processing Time", alpha=0.6)
# plt.scatter(data["model"], data["image_processing_time"], label="Image Processing Time", alpha=0.6)
plt.title("Processing Times Compared to Model")
plt.xlabel("YOLO Model")
plt.ylabel("Processing Time (s)")
plt.legend()
plt.grid()
plt.show()

# Plot 3: Correlation analysis
correlation_data = data[["model_weight", "model_processing_time", "image_processing_time"]].dropna()
correlations = correlation_data.corr()

# Display correlation matrix
plt.figure(figsize=(8, 6))
plt.matshow(correlations, fignum=1, cmap="coolwarm")
plt.colorbar()
plt.xticks(range(len(correlations.columns)), correlations.columns, rotation=45, ha="left")
plt.yticks(range(len(correlations.columns)), correlations.columns)
plt.title("Correlation Matrix of Model and Processing Times", pad=20)
plt.show()

# Print correlation values
print("Correlation Matrix:")
print(correlations)
