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
        # self.exemplar = exemplar
        self.count = 0
        self.time = -1  # For tracking when thresholds are violated
        self.thresholds = _load_thresholds()

    def get_ideal_model(self, input_rate):
        for model in ["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"]:
            rate_min = self.thresholds[f"{model}_rate_min"]
            rate_max = self.thresholds[f"{model}_rate_max"]
            if rate_min <= input_rate <= rate_max:
                print(f"Model: {model} for rate {input_rate} between min {rate_min} max {rate_max}")
                return model
        print("No ideal model found")
        return None

    def analyze(self):
        print("Analyzing")
        # Get monitoring data
        data = switch.get_monitor_data()
        input_rate = data["input_rate"]
        model = data["model"]
        self.knowledge.analysis_data['input_rate'] = input_rate
        self.knowledge.analysis_data['current_model'] = model
        print(input_rate)

        # Get threshold keys for the current model
        str_min = f"{model}_rate_min"
        str_max = f"{model}_rate_max"

        # Fetch min and max thresholds
        min_val = self.thresholds.get(str_min)
        max_val = self.thresholds.get(str_max)
        current_time = time.time()

        # Check if the input rate violates thresholds
        if not (min_val <= input_rate <= max_val):
            print("thresholds violated")
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
        model = self.knowledge.analysis_data['current_model']

        ideal_model = self.get_ideal_model(input_rate)
        print("ideal model", ideal_model, "model", model)
        if ideal_model is not None and ideal_model != model:
            self.knowledge.analysis_data['ideal_model'] = ideal_model
            print(f"Switching from model {model} to {ideal_model}")
            self.knowledge.plan_data = {"model": ideal_model}
            return True
        self.knowledge.plan_data = {"model": model}
        return True