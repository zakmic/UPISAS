import csv
import os
from collections import Counter

from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import time
import statistics

from UPISAS.exemplars.switch_exemplar import SwitchExemplar
from UPISAS.experiment_runner_configs.SwitchAPI import upload_files
from UPISAS.strategies.BaselineSwitchStrategy import SwitchStrategy


class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name: str = "new_runner_experiment"

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path: Path = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type: OperationType = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms: int = 1000

    exemplar = None
    strategy = None

    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment)
        ])
        self.run_table_model = None  # Initialized later
        self.total_imgs = 10  # Smaller Experiment
        # self.total_imgs = 300  # Actual dataset was 300

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""

        factor1 = FactorModel("input_rate", [2, 0.5, 0.05])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            exclude_variations=[
            ],
            data_columns=['utility', 'cpu_utility']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        self.exemplar = SwitchExemplar(auto_start=True)
        self.strategy = SwitchStrategy(self.exemplar)
        time.sleep(3)

        # Require user interaction before proceeding to the next run
        # input("Reload the dataset. Start processing on Switch then press Enter to start the next experiment run...")
        input(
            "Make sure the frontend, kibana and elastic search are already running!! The backend will start automatically. Press ENTER to continue")

        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""
        # self.strategy.RT_THRESHOLD = float(context.run_variation['rt_threshold'])

        output.console_log("start_run begin")
        self.exemplar.start_run()
        time.sleep(3)
        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""
        # TODO Create method that polls until turns on
        # self.strategy.get_monitor_schema()
        # self.strategy.get_adaptation_options_schema()
        # self.strategy.get_execute_schema()
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""
        time_slept = 0
        done = False
        # Endpoint URL
        endpoint = "http://localhost:3001/api/upload"

        # File paths
        csv_path = "UPISAS/experiment_runner_configs/upload/var_rate_300.csv"
        zip_path = "UPISAS/experiment_runner_configs/upload/animals.zip"

        time.sleep(10)

        upload_files(endpoint, csv_path, zip_path)

        while done == False:
            self.strategy.monitor(verbose=True)
            current_img = self.strategy.knowledge.monitored_data["log_id"][-1]
            print("LOG_ID", current_img)
            if self.strategy.analyze():
                    self.strategy.plan()
                    # if self.strategy.knowledge.plan_data is not None:
                    #     self.strategy.execute()
                    # else:
                    #     print("MAPE-K Loop: No adaptation")
            time.sleep(1)
            time_slept += 1
            done = current_img == self.total_imgs

        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""

        output.console_log("Config.stop_measurement called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        self.exemplar.stop_container()

        output.console_log("You can end the current run. Manually starting the next run is required")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`.
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated."""

        output.console_log("Config.populate_run_data() called!")

        basicRevenue = 1
        optRevenue = 1.5
        serverCost = 10

        precision = 1e-5
        data = self.strategy.knowledge.monitored_data
        utilities = []

        # Extract data fields for calculation
        input_rate = data.get("input_rate", [])
        confidence = data.get("confidence", [])
        absolute_time_from_start = data.get("absolute_time_from_start", [])
        cpu_utility = data.get("cpu", [])
        detection_boxes = data.get("detection_boxes", [])
        model_processing_time = data.get("model_processing_time", [])
        image_processing_time = data.get("image_processing_time", [])
        utility = data.get("utility", [])
        models = data.get("model", [])
        model_name = data.get("model_name", [])
        timestamp = data.get("timestamp", [])
        log = data.get("log_id", [])

        # Count occurrences of each model
        model_counts = Counter(models)

        # Prepare CSV file name
        csv_filename = "run.csv"

        # Write every log entry to CSV file
        try:
            write_header = not os.path.exists(csv_filename)

            with open(csv_filename, mode='a', newline='') as csv_file:
                fieldnames = [
                    "image", "timestamp", "input_rate", "confidence", "absolute_time_from_start", "cpu_utility",
                    "detection_boxes", "model_processing_time", "image_processing_time",
                    "utility", "model",
                ]

                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                if write_header:
                    writer.writeheader()  # Write header only if the file is new

                # Write each log entry to CSV
                for i in range(len(confidence)):
                    log_entry = {
                        "image": log[i] if i < len(log) else None,
                        "timestamp": timestamp[i] if i < len(timestamp) else None,
                        "input_rate": input_rate[i] if i < len(input_rate) else None,
                        "confidence": confidence[i] if i < len(confidence) else None,
                        "absolute_time_from_start": absolute_time_from_start[i] if i < len(
                            absolute_time_from_start) else None,
                        "cpu_utility": cpu_utility[i] if i < len(cpu_utility) else None,
                        "detection_boxes": detection_boxes[i] if i < len(detection_boxes) else None,
                        "model_processing_time": model_processing_time[i] if i < len(model_processing_time) else None,
                        "image_processing_time": image_processing_time[i] if i < len(image_processing_time) else None,
                        "utility": utility[i] if i < len(utility) else None,
                        "model": models[i] if i < len(models) else None
                    }
                    writer.writerow(log_entry)

                # Append a dotted line separator only once at the end of all log entries for the current run
                writer.writerow({field: "----" for field in fieldnames})

        except Exception as e:
            output.console_log(f"Error writing to CSV {csv_filename}: {e}")

        # Print data for debugging
        print("Data:", data)
        print("Averages:")
        print(f"Confidence: {confidence}")
        print(f"CPU Utility: {cpu_utility}")
        print("Model Counts:", model_counts)

        return {
            "confidence": sum(confidence) / len(confidence) if confidence else 0,
            "absolute_time_from_start": sum(absolute_time_from_start) / len(
                absolute_time_from_start) if absolute_time_from_start else 0,
            "cpu_utility": sum(cpu_utility) / len(cpu_utility) if cpu_utility else 0,
            "detection_boxes": sum(detection_boxes) / len(detection_boxes) if detection_boxes else 0,
            "model_processing_time": sum(model_processing_time) / len(
                model_processing_time) if model_processing_time else 0,
            "image_processing_time": sum(image_processing_time) / len(
                image_processing_time) if image_processing_time else 0,
            "utility": sum(utility) / len(utility) if utility else 0,
            "model_counts": dict(model_counts)  # Return model counts for reference
        }

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path: Path = None
