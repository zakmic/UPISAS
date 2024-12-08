import requests
import os


def upload_files(endpoint_url, csv_file_path, zip_file_path, approach="NAIVE"):
    """
    Sends a CSV file and a zipped image folder to the specified endpoint.

    :param endpoint_url: URL of the endpoint (e.g., 'http://localhost:8000/api/upload').
    :param csv_file_path: Path to the CSV file to upload.
    :param zip_file_path: Path to the zipped folder to upload.
    :param approach: Approach type (e.g., 'AdaMLs', 'NAIVE', etc.).
    :return: Response from the server.
    """
    try:
        # Prepare the payload
        files = {
            "csvFile": open(csv_file_path, "rb"),  # Required CSV file
            "approch": (None, approach),  # Form field
        }

        # Add the zip file if provided
        if zip_file_path:
            files["zipFile"] = open(zip_file_path, "rb")

        # Send the POST request
        print(f"Sending request to {endpoint_url}...")
        response = requests.post(endpoint_url, files=files)

        # Close the file handlers
        for file in files.values():
            if isinstance(file, tuple):
                continue
            file.close()

        # Check the response
        if response.status_code == 200:
            print("Files uploaded and processed successfully!")
            print("Response:", response.json())
        else:
            print("Failed to upload files.")
            print("Status Code:", response.status_code)
            print("Response:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))
