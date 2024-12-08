import os
import time
import pandas as pd
from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch_interface as switch

# Global thresholds for analysis
THRESHOLDS = {
    "cpu_utilization": {"upper": 80, "lower": 20},  # percent
    "confidence": {"lower": 0.5},  # minimum confidence level
    "processing_time": {"upper": 2}  # seconds per image
}

def model_to_option(model):
    """
    Maps YOLO model names to corresponding option numbers.
    """
    model_map = {'yolov5n': 1, 'yolov5s': 2, 'yolov5m': 3, 'yolov5l': 4, 'yolov5x': 5}
    return model_map.get(model, -1)

class SwitchStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.count = 0
        self.time = -1  # For tracking when thresholds are violated
        self.adaptation_needed = None  # Initialize adaptation_needed

    def analyze(self):
        print("Analyzing")
        # Get monitoring data
        data = switch.get_monitor_data()
        input_rate = data["input_rate"]
        cpu_utilization = data["cpu"]
        confidence = data["confidence"]
        image_processing_time = data["image_processing_time"]
        model_processing_time = data["model_processing_time"]
        model = data["model"]
        utility = data["utility"]

        # Store data for further use
        # self.knowledge.analysis_data['input_rate'] = input_rate
        # self.knowledge.analysis_data['cpu'] = cpu_utilization
        self.knowledge.analysis_data['model'] = model
        # self.knowledge.analysis_data['confidence'] = confidence
        # self.knowledge.analysis_data['image_processing_time'] = image_processing_time
        # self.knowledge.analysis_data['model_processing_time'] = model_processing_time

        # print(f"Input Rate: {input_rate}, CPU Utilization: {cpu_utilization}, "
        #       f"Confidence: {confidence}, Image Processing Time: {image_processing_time}, "
        #       f"Model Processing Time: {model_processing_time}, Model: {model}")

        # Check thresholds
        current_time = time.time()
        _pending_adaptation = None

        # Determine if adaptation is needed
        if (cpu_utilization > THRESHOLDS["cpu_utilization"]["upper"]) or \
                (model_processing_time > THRESHOLDS["processing_time"]["upper"]) or \
                (confidence < THRESHOLDS["confidence"]["lower"]):
            _pending_adaptation = 'smaller'
        elif (cpu_utilization < THRESHOLDS["cpu_utilization"]["lower"]) or \
                (confidence >= THRESHOLDS["confidence"]["lower"] and
                 model_processing_time <= THRESHOLDS["processing_time"]["upper"]):
            _pending_adaptation = 'larger'

        if _pending_adaptation:
            print(f"Thresholds violate detected, need to switch to {_pending_adaptation} model.")
            if self.time == -1:
                # First detection, start timing
                self.time = current_time
            elif (current_time - self.time) > 0.25:
                # Violation persisted, proceed with adaptation
                self.adaptation_needed = _pending_adaptation  # Now set adaptation_needed
                self.count += 1
                print({'Component': "Analyzer", "Action": "Creating adaptation plan"})
        else:
            self.time = -1
            self.adaptation_needed = None
            _pending_adaptation = None

        return True

    def plan(self):
        print("Planning")
        new_model_index = -1
        if self.adaptation_needed:
            model = self.knowledge.analysis_data['model']
            model_index = model_to_option(model)

            if self.adaptation_needed == 'smaller' and model_index > 1:
                new_model_index = max(1, model_index - 1)
            elif self.adaptation_needed == 'larger' and model_index < 5:
                new_model_index = min(5, model_index + 1)
            else:
                print(f"Current model is already the {self.adaptation_needed} model, no need to change.")
                new_model_index = model_index

            if new_model_index != model_index:
                print(f"Switching model from {model} to {self.adaptation_needed}.")
                # Store the plan to switch model
                self.knowledge.plan_data = {'model_option': new_model_index}
            else:
                print("No adaptation needed as the current model is already optimal.")
                self.knowledge.plan_data = None
        else:
            print("No adaptation needed")
            self.knowledge.plan_data = None

        return True
