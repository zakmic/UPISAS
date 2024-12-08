from UPISAS.strategies.helpers.predict import predict_future_metrics
from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch_interface as switch
import optuna

# Global thresholds for analysis
THRESHOLDS = {
    "cpu_utilization": {"upper": 80, "lower": 20},  # percent
    "confidence": {"lower": 0.5},  # minimum confidence level
    "processing_time": {"upper": 2}  # seconds per image
}

class SwitchStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.count = 0
        self.time = -1  # For tracking when thresholds are violated
        self.adaptation_needed = None
        self.metric_history = []
        self.study = optuna.create_study(direction='maximize')

    def optimize_thresholds(self):
        def objective(trial):
            # Define hyperparameters (thresholds) to be optimized
            cpu_utilization_upper = trial.suggest_int("cpu_utilization_upper", 50, 100)
            cpu_utilization_lower = trial.suggest_int("cpu_utilization_lower", 0, 30)
            confidence_lower = trial.suggest_float("confidence_lower", 0.3, 1.0)
            processing_time_upper = trial.suggest_int("processing_time_upper", 1, 5)

            # Update thresholds for this trial
            self.thresholds = {
                "cpu_utilization": {"upper": cpu_utilization_upper, "lower": cpu_utilization_lower},
                "confidence": {"lower": confidence_lower},
                "processing_time": {"upper": processing_time_upper}
            }

            # Calculate cumulative utility over the simulated iterations
            total_utility = sum(metric['utility'] for metric in self.metric_history)
            return -total_utility  # Minimize negative utility

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)  # Adjust n_trials as needed

        # Update thresholds with the best found values
        best_params = study.best_params
        self.thresholds = {
            "cpu_utilization": {"upper": best_params["cpu_utilization_upper"], "lower": best_params["cpu_utilization_lower"]},
            "confidence": {"lower": best_params["confidence_lower"]},
            "processing_time": {"upper": best_params["processing_time_upper"]}
        }

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
            "cpu_utilization": cpu_utilization,
            "confidence": confidence,
            "image_processing_time": image_processing_time,
            "model_processing_time": model_processing_time,
            "utility": utility
        })

        # Once we have 20 entries, predict metrics for 10 seconds from now
        if len(self.metric_history) == 20:
            predicted_metrics = predict_future_metrics(self.metric_history, horizon=10)
            cpu_utilization = predicted_metrics["cpu"]
            confidence = predicted_metrics["confidence"]
            image_processing_time = predicted_metrics["image_processing_time"]
            model_processing_time = predicted_metrics["model_processing_time"]


        # Check if adaptation is needed based on optimized thresholds
        _pending_adaptation = None
        if (cpu_utilization > self.thresholds["cpu_utilization_upper"]) or \
                (image_processing_time > self.thresholds["processing_time_upper"]) or \
                (confidence < self.thresholds["confidence_lower"]):
            _pending_adaptation = "smaller"
        elif (cpu_utilization < self.thresholds["cpu_utilization_lower"]) and \
                (confidence >= self.thresholds["confidence_lower"]) and \
                (image_processing_time <= self.thresholds["processing_time_upper"]):
            _pending_adaptation = "larger"

        if _pending_adaptation:
            print(f"Thresholds violated, need to switch to {_pending_adaptation} model.")
            self.adaptation_needed = _pending_adaptation
        else:
            self.adaptation_needed = None

        return True

    def plan(self):
        print("Planning")
        if self.adaptation_needed:
            best_model_name = self.knowledge.analysis_data['best_model']
            new_model_index = model_to_option(best_model_name)
            current_model = self.knowledge.analysis_data['model']
            current_model_index = model_to_option(current_model)

            if new_model_index != current_model_index:
                print(f"Switching model from {current_model} to {best_model_name}.")
                # Store the plan to switch model
                self.knowledge.plan_data = {'model_option': new_model_index}
            else:
                print("No adaptation needed as the current model is already optimal.")
                self.knowledge.plan_data = None
        else:
            print("No adaptation needed")
            self.knowledge.plan_data = None

        return True