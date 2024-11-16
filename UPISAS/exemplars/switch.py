# api_client.py

import requests

# Base URL of the FastAPI application
base_url = "http://localhost:8000"

def get_monitor_data():
    url = f"{base_url}/monitor"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as err:
        raise Exception(f"HTTP error occurred: {err} - {response.text}")
    except Exception as err:
        raise Exception(f"An error occurred: {err}")

def get_adaptation_options():
    url = f"{base_url}/adaptation_options"
    try:
        response = requests.get(url)
        response.raise_for_status()
        options = response.json()
        return options
    except requests.exceptions.HTTPError as err:
        raise Exception(f"HTTP error occurred: {err} - {response.text}")
    except Exception as err:
        raise Exception(f"An error occurred: {err}")

def execute_action(option, new_value):
    url = f"{base_url}/execute"
    params = {
        'option': option,
        'new_value': new_value
    }
    try:
        response = requests.put(url, params=params)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.HTTPError as err:
        raise Exception(f"HTTP error occurred: {err} - {response.text}")
    except Exception as err:
        raise Exception(f"An error occurred: {err}")

if __name__ == "__main__":
    # Get Monitor Data
    data = get_monitor_data()
    print("Monitor Data:")
    print(data)

    # Get Adaptation Options
    options = get_adaptation_options()
    print("\nAdaptation Options:")
    print(options)

    # Execute Action
    # Example: Update 'yolov5n_rate_min' to a new value of 0.5
    option_to_update = 'yolov5n_rate_min'
    new_value = 0.5
    result = execute_action(option_to_update, new_value)
    print("\nExecute Action Response:")
    print(result)
