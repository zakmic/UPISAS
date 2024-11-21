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
from UPISAS.strategies.SwitchStrategy import SwitchStrategy
from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.exemplars.swim import SWIM


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
        self.total_imgs = 25 # Total number of images in the experiment

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        # 2 should choose yolo yolov5n using NAIVE
        # 10 should choose yolo yolov5m using NAIVE
        # 30 should choose yolo yolov5x using NAIVE

        factor1 = FactorModel("input_rate", [2, 10, 30])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            exclude_variations=[
            ],
            data_columns=['time_to_process', 'cpu_utility', 'confidence']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        self.exemplar = SwitchExemplar()
        self.strategy = SwitchStrategy(self.exemplar)
        time.sleep(3)

        # Require user interaction before proceeding to the next run
        input("Reload the dataset. Start processing on Switch then press Enter to start the next experiment run...")

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
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""
        time_slept = 0
        self.strategy.get_monitor_schema()
        self.strategy.get_adaptation_options_schema()
        self.strategy.get_execute_schema()
        done = False

        while done == False:
            self.strategy.monitor(verbose=True)
            current_img = self.strategy.knowledge.monitored_data["log_id"][-1]
            print("LOG_ID", current_img)
            if self.strategy.analyze():
                    self.strategy.plan()
                    # self.strategy.execute() To be done in Ass 2
            time.sleep(3)
            time_slept += 3
            done = current_img == self.total_imgs

        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""

        output.console_log("Config.stop_measurement called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        # self.exemplar.stop_container()

        output.console_log("You can end the current run. Manually starting the next run is required")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`.
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated."""

        output.console_log("Config.populate_run_data() called!")

        # Get monitored data
        data = self.strategy.knowledge.monitored_data

        # Extract data fields for calculation
        confidence = data.get("confidence", [])
        time_to_process = data.get("absolute_time_from_start", [])
        cpu_utility = data.get("cpu", [])
        detection_boxes = data.get("detection_boxes", [])
        model_processing_time = data.get("model_processing_time", [])
        image_processing_time = data.get("image_processing_time", [])
        utility = data.get("utility", [])
        models = data.get("model", [])

        # Calculate averages for numerical fields
        avg_confidence = sum(confidence) / len(confidence) if confidence else 0
        avg_time_to_process = sum(time_to_process) / len(time_to_process) if time_to_process else 0
        avg_cpu_utility = sum(cpu_utility) / len(cpu_utility) if cpu_utility else 0
        avg_detection_boxes = sum(detection_boxes) / len(detection_boxes) if detection_boxes else 0
        avg_model_processing_time = sum(model_processing_time) / len(
            model_processing_time) if model_processing_time else 0
        avg_image_processing_time = sum(image_processing_time) / len(
            image_processing_time) if image_processing_time else 0
        avg_utility = sum(utility) / len(utility) if utility else 0

        # Count occurrences of each model
        model_counts = Counter(models)

        # Prepare data dictionary for CSV and return
        run_data = {
            "confidence": avg_confidence,
            "time_to_process": avg_time_to_process,
            "cpu_utility": avg_cpu_utility,
            "detection_boxes": avg_detection_boxes,
            "model_processing_time": avg_model_processing_time,
            "image_processing_time": avg_image_processing_time,
            "utility": avg_utility,
            "model_counts": dict(model_counts)  # Converting Counter to dict for easier serialization
        }

        csv_filename = f"run.csv"

        # Write to CSV file
        try:
            # Check if the file exists to determine if we need to write the header
            write_header = not os.path.exists(csv_filename)

            with open(csv_filename, mode='a', newline='') as csv_file:
                fieldnames = ["confidence", "time_to_process", "cpu_utility", "detection_boxes",
                              "model_processing_time", "image_processing_time", "utility", "model_counts"]

                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()  # Write header only if the file is new
                flattened_run_data = {key: run_data[key] if key != "model_counts" else str(run_data[key])
                                      for key in run_data}
                writer.writerow(flattened_run_data)

        except Exception as e:
            output.console_log(f"Error writing to CSV {csv_filename}: {e}")

        print("Data:", data)
        print("Averages:")
        print(f"Confidence: {avg_confidence}, Time to Process: {avg_time_to_process}, CPU Utility: {avg_cpu_utility}")
        print(f"Detection Boxes: {avg_detection_boxes}, Model Processing Time: {avg_model_processing_time}")
        print(f"Image Processing Time: {avg_image_processing_time}, Utility: {avg_utility}")
        print("Model Counts:", model_counts)

        return {
            "confidence": avg_confidence,
            "time_to_process": avg_time_to_process,
            "cpu_utility": avg_cpu_utility,
            "detection_boxes": avg_detection_boxes,
            "model_processing_time": avg_model_processing_time,
            "image_processing_time": avg_image_processing_time,
            "utility": avg_utility,
            "model_counts": dict(model_counts)  # Return model counts for reference
        }

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path: Path = None
