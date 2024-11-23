import os
import time
import pandas as pd
from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch_interface as switch


def _load_thresholds():
    print("Current working directory:", os.getcwd())
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
        confidence = data["confidence"]
        processing_time = data["image_processing_time"]
        model = data["model"]

        # Store data for further use
        self.knowledge.analysis_data['input_rate'] = input_rate
        self.knowledge.analysis_data['cpu'] = cpu_utilization
        self.knowledge.analysis_data['model'] = model
        self.knowledge.analysis_data['confidence'] = confidence
        self.knowledge.analysis_data['image_processing_time'] = processing_time

        print(f"Input Rate: {input_rate}, CPU Utilization: {cpu_utilization}, Confidence: {confidence}, Processing Time: {processing_time}, Model: {model}")

        alpha_cpu, alpha_conf, alpha_pt = 0.5, 0.25, 0.25
        gamma = (cpu_utilization * alpha_cpu - confidence * alpha_conf + processing_time * alpha_pt)
        print(f"Effectiveness Metric (Gamma): {gamma}")

        str_min = f"{model}_rate_min"
        str_max = f"{model}_rate_max"

        min_val = self.thresholds.get(str_min)
        max_val = self.thresholds.get(str_max)
        current_time = time.time()

        # Check if the input rate violates thresholds or if CPU utilization is too high
        threshold_violation = not (min_val <= input_rate <= max_val)
        high_cpu_utilization = cpu_utilization > 80
        low_effectiveness = gamma > 1.0

        if threshold_violation or high_cpu_utilization or low_effectiveness:
            print("Thresholds violated, CPU utilization too high, or low effectiveness detected")
            if self.time == -1:
                self.time = current_time
            elif (current_time - self.time) > 0.25:  # Threshold violation persists
                self.count += 1
                print({'Component': "Analyzer", "Action": "Creating adaptation plan"})
        else:
            self.time = -1

        return True

    def plan(self):
        print("Planning")
        input_rate = self.knowledge.analysis_data['input_rate']
        cpu_utilization = self.knowledge.analysis_data['cpu']
        model = self.knowledge.analysis_data['model']

        # Adapt thresholds based on analysis data
        new_min_threshold = input_rate * 0.9 if cpu_utilization > 80 else input_rate * 0.95
        new_max_threshold = input_rate * 1.1 if cpu_utilization > 80 else input_rate * 1.05

        # Ensure the values make logical sense for adaptation
        new_min_threshold = max(0, new_min_threshold)

        # Create plan_data entries compatible with the execute schema
        self.knowledge.plan_data = [
            {"option": f"{model}_rate_min", "new_value": new_min_threshold},
            {"option": f"{model}_rate_max", "new_value": new_max_threshold}
        ]

        print(f"Plan to update thresholds for {model}:")
        print(f"New Min Threshold: {new_min_threshold}, New Max Threshold: {new_max_threshold}")

        return True
