import time

from optuna.samplers import RandomSampler

from UPISAS.strategies.helpers.predict import predict_future_metrics
from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch_interface as switch
import optuna


def model_to_option(model):
    """
    Maps YOLO model names to corresponding option numbers.
    """
    model_map = {'yolov5n': 1, 'yolov5s': 2, 'yolov5m': 3, 'yolov5l': 4, 'yolov5x': 5}
    return model_map.get(model, -1)

class SwitchStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.predict = True
        self.count = 0
        self.time = -1  # For tracking when thresholds are violated
        self.adaptation_needed = None
        self.metric_history = []
        self.thresholds = {
            "cpu_utilization_upper": 80,
            "cpu_utilization_lower": 20,
            "confidence_lower": 0.5,
            "processing_time_upper": 2
        }
        self.study = optuna.create_study(direction="maximize",sampler=RandomSampler())  # Random Sampler for increased exploration

    def analyze(self):
        print("Analyzing")
        # Get monitoring data
        data = switch.get_monitor_data()
        input_rate = data["input_rate"]
        cpu_utilization = data["cpu"]
        confidence = data["confidence"]
        image_processing_time = data["image_processing_time"]
        model_processing_time = data["model_processing_time"]
        current_model = data["model"]
        utility = data["utility"]

        # Store data for further use
        self.knowledge.analysis_data['model'] = current_model

        # Append to metric history
        self.metric_history.append({
            "cpu": cpu_utilization,
            "confidence": confidence,
            "image_processing_time": image_processing_time,
            "model_processing_time": model_processing_time,
            "utility": utility
        })

        # Once we have 20 entries, predict metrics for 10 seconds from now
        if self.predict == True and len(self.metric_history) == 20:
            predicted_metrics = predict_future_metrics(self.metric_history, horizon=10)
            cpu_utilization = predicted_metrics["cpu"]
            confidence = predicted_metrics["confidence"]
            image_processing_time = predicted_metrics["image_processing_time"]
            model_processing_time = predicted_metrics["model_processing_time"]

        # Increment the counter
        self.count += 1

        # Optimize thresholds every 10 iterations
        if self.count % 10 == 0 and len(self.metric_history) > 0:
            self.study.optimize(self.optimize_tresholds, n_trials=5)
            self.thresholds = self.study.best_params
            print(f"Updated thresholds: {self.thresholds}")

        # Check thresholds
        current_time = time.time()
        _pending_adaptation = None

        # First, check confidence violation
        if confidence < self.thresholds["confidence_lower"]:
            _pending_adaptation = 'larger'
            print("Confidence below threshold, need to switch to a larger model.")
        else:
            # Next, check model processing time violation
            if model_processing_time > self.thresholds["processing_time_upper"]:
                _pending_adaptation = 'smaller'
                print("Model processing time above threshold, need to switch to a smaller model.")
            else:
                # Next, check CPU utilization violation
                if cpu_utilization > self.thresholds["cpu_utilization_upper"]:
                    _pending_adaptation = 'smaller'
                    print("CPU utilization above upper threshold, need to switch to a smaller model.")
                elif cpu_utilization < self.thresholds["cpu_utilization_lower"]:
                    _pending_adaptation = 'larger'
                    print("CPU utilization below lower threshold, can switch to a larger model.")
                else:
                    # No adaptation needed
                    self.adaptation_needed = None
                    self.time = -1
                    print("No thresholds violated, no adaptation needed.")
                    return True  # Exit analyze method

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
                print(f"Switching model from {model} to {self.adaptation_needed} {new_model_index}")
                # Store the plan to switch model
                self.knowledge.plan_data = {'model_option': new_model_index}
            else:
                print("No adaptation needed as the current model is already optimal.")
                self.knowledge.plan_data = None
        else:
            print("No adaptation needed")
            self.knowledge.plan_data = None

        return True

    def optimize_tresholds(self, trial):
        # Suggest thresholds dynamically
        cpu_upper = trial.suggest_float("cpu_utilization_upper", 75, 95)
        cpu_lower = trial.suggest_float("cpu_utilization_lower", 10, 60)
        confidence_lower = trial.suggest_float("confidence_lower", 0.3, 0.95)
        processing_time_upper = trial.suggest_float("processing_time_upper", 1, 5)

        # Evaluate utility using all historical data
        total_utility = 0
        for record in self.metric_history:  # Use all historical data
            if (record["cpu"] <= cpu_upper and record["cpu"] >= cpu_lower and
                record["confidence"] >= confidence_lower and
                record["image_processing_time"] <= processing_time_upper):
                total_utility += record["utility"] * (record["confidence"] ** 2)

        return total_utility