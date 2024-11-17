from UPISAS.exemplar import Exemplar
import UPISAS.exemplars.switch_interface as switch_interface

class SwitchExemplar(Exemplar):
    def __init__(self, auto_start=False):
        self.start_run(self)
        self.base_endpoint = "http://localhost:8000"
        # docker_config = {
        #     "name":  "switch",
        #     "image": "switch-backend:latest",
        #     "ports" : {8000: 8000}}
        #
        # super().__init__("http://localhost:8000", docker_config, auto_start)

    def start_run(self):
        self.API = switch_interface
        try:
            self.monitor_data = switch_interface.get_monitor_data()
            assert self.monitor_data is not None, "Monitor data should not be None"
            print("API is up and running.")
        except Exception as e:
            raise Exception(f"API is not running or /monitor endpoint failed during setUpClass: {e}")

    def start_run(self, app):
        print("ARGHHH")
        self.API = switch_interface
        try:
            self.monitor_data = switch_interface.get_monitor_data()
            assert self.monitor_data is not None, "Monitor data should not be None"
            print("API is up and running.")
        except Exception as e:
            raise Exception(f"API is not running or /monitor endpoint failed during setUpClass: {e}")
