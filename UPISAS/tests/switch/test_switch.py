# test_strategy.py

import unittest
import UPISAS.exemplars.switch as switch

class TestStrategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Verify that the API is up and running by calling get_monitor_data
        try:
            cls.monitor_data = switch.get_monitor_data()
            assert cls.monitor_data is not None, "Monitor data should not be None"
            print("API is up and running.")
        except Exception as e:
            raise Exception(f"API is not running or /monitor endpoint failed during setUpClass: {e}")

    def test_monitor_successfully(self):
        data = switch.get_monitor_data()
        self.assertTrue(len(data) > 0, "Monitor data should not be empty")
        # Optionally, check for expected keys
        expected_keys = ["input_rate", "model"]
        for key in expected_keys:
            print(key, data[key])
            self.assertIn(key, data, f"Key '{key}' not found in monitor data")

    def test_get_adaptation_options(self):
        """Test that adaptation options are retrieved successfully."""
        options = switch.get_adaptation_options()
        self.assertIsNotNone(options, "Adaptation options should not be None")
        self.assertIsInstance(options, dict, "Adaptation options should be a dictionary")
        self.assertTrue(len(options) > 0, "Adaptation options should not be empty")
        # Check for expected adaptation options
        expected_options = [
            "yolov5n_rate_min", "yolov5n_rate_max",
            "yolov5s_rate_min", "yolov5s_rate_max",
            "yolov5m_rate_min", "yolov5m_rate_max",
            "yolov5l_rate_min", "yolov5l_rate_max",
            "yolov5x_rate_min", "yolov5x_rate_max"
        ]
        for option in expected_options:
            self.assertIn(option, options, f"Option '{option}' not found in adaptation options")

    def test_execute_action(self):
        """Test that an adaptation option can be updated successfully."""
        option_to_update = 'yolov5n_rate_min'
        new_value = 0.5
        result = switch.execute_action(option_to_update, new_value)
        self.assertIn('message', result, "Response does not contain 'message'")
        self.assertIn("updated to", result['message'], "Update confirmation not found in response message")
        # Verify that the adaptation option was updated
        options = switch.get_adaptation_options()
        updated_value = float(options.get(option_to_update))
        self.assertEqual(
            updated_value, new_value,
            f"Adaptation option '{option_to_update}' expected to be {new_value}, but got {updated_value}"
        )



if __name__ == '__main__':
    unittest.main()
