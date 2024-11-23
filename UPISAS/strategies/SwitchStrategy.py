import time
import pandas as pd
from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch_interface as switch


def _load_thresholds():
    df = pd.read_csv('knowledge.csv', header=None)
    array = df.to_numpy()

    return {
        "yolov5n_rate_min": array[0][1],
        "yolov5n_rate_max": array[0][2],
        "yolov5s_rate_min": array[1][1],
        "yolov5s_rate_max": array[1][2],
        "yolov5m_rate_min": array[2][1],
        "yolov5m_rate_max": array[2][2],
        "yolov5l_rate_min": array[3][1],
        "yolov5l_rate_max": array[3][2],
        "yolov5x_rate_min": array[4][1],
        "yolov5x_rate_max": array[4][2],
    }


class SwitchStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.count = 0
        self.time = -1  # For tracking when thresholds are violated
        self.thresholds = _load_thresholds()

    def analyze(self):
        print("Analyzing")
        # Get monitoring data
        data = switch.get_monitor_data()
        input_rate = data["input_rate"]
        cpu_utilization = data["cpu"]
        model = data["model"]

        # Store data for further use
        self.knowledge.analysis_data['input_rate'] = input_rate
        self.knowledge.analysis_data['cpu'] = cpu_utilization
        self.knowledge.analysis_data['model'] = model

        print(f"Input Rate: {input_rate}, CPU Utilization: {cpu_utilization}")

        # Get threshold keys for the current model
        str_min = f"{model}_rate_min"
        str_max = f"{model}_rate_max"

        # Fetch min and max thresholds
        min_val = self.thresholds.get(str_min)
        max_val = self.thresholds.get(str_max)
        current_time = time.time()

        # Check if the input rate violates thresholds or if CPU utilization is too high
        threshold_violation = not (min_val <= input_rate <= max_val)
        high_cpu_utilization = cpu_utilization > 80  # Assume 80% CPU usage is a high threshold

        # Track time for threshold violation persistence
        if threshold_violation or high_cpu_utilization:
            print("Thresholds violated or CPU utilization too high")
            if self.time == -1:
                self.time = current_time
            elif (current_time - self.time) > 0.25:  # Threshold violation persists
                self.count += 1
                print({'Component': "Analyzer", "Action": "Creating adaptation plan"})
        else:
            self.time = -1  # Reset the timer if thresholds are not violated

        return True

    def plan(self):
        print("Planning")
        input_rate = self.knowledge.analysis_data['input_rate']
        cpu_utilization = self.knowledge.analysis_data['cpu']
        model = self.knowledge.analysis_data['model']

        # Adapt thresholds based on analysis data
        # Adjust threshold based on CPU utilization or input rate analysis
        new_min_threshold = input_rate * 0.9 if cpu_utilization > 80 else input_rate * 0.95
        new_max_threshold = input_rate * 1.1 if cpu_utilization > 80 else input_rate * 1.05

        # Ensure the values make logical sense for adaptation
        new_min_threshold = max(0, new_min_threshold)  # Minimum cannot be less than 0

        # Create plan_data entries compatible with the execute schema
        self.knowledge.plan_data = [
            {"option": f"{model}_rate_min", "new_value": new_min_threshold},
            {"option": f"{model}_rate_max", "new_value": new_max_threshold}
        ]

        print(f"Plan to update thresholds for {model}:")
        print(f"New Min Threshold: {new_min_threshold}, New Max Threshold: {new_max_threshold}")

        return True
