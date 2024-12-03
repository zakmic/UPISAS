import numpy as np
from sklearn.linear_model import LinearRegression

def predict_future_metrics(metric_history, horizon=10):
    """
    Predict future metrics based on the past metric history.

    Args:
        metric_history (list of dicts): The previous metric history (last 50 entries).
        horizon (int): Number of seconds into the future to predict.

    Returns:
        dict: Predicted metrics for 'cpu', 'confidence', 'image_processing_time', and 'model_processing_time'.
    """
    print("predicting values")
    # Extract the individual metric lists from the history
    cpu_history = [entry['cpu'] for entry in metric_history]
    confidence_history = [entry['confidence'] for entry in metric_history]
    image_processing_time_history = [entry['image_processing_time'] for entry in metric_history]
    model_processing_time_history = [entry['model_processing_time'] for entry in metric_history]

    # Prepare input data for prediction
    X = np.array(range(len(metric_history))).reshape(-1, 1)
    future_X = np.array([[len(metric_history) + horizon - 1]])

    # Function to fit and predict the future value using linear regression
    def predict_next_value(y_history):
        model = LinearRegression()
        model.fit(X, y_history)
        return model.predict(future_X)[0]

    # Predict future values for each metric
    predicted_cpu = predict_next_value(cpu_history)
    predicted_confidence = predict_next_value(confidence_history)
    predicted_image_processing_time = predict_next_value(image_processing_time_history)
    predicted_model_processing_time = predict_next_value(model_processing_time_history)

    # Return the predicted metrics
    return {
        "cpu": predicted_cpu,
        "confidence": predicted_confidence,
        "image_processing_time": predicted_image_processing_time,
        "model_processing_time": predicted_model_processing_time
    }
