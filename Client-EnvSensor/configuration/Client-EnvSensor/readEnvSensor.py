import requests
import os
import csv

SERVER = "http://192.168.103.20"
OUTPUT_DIR = "/app/logs"
FILE_LIMIT = 289 # i.e. keep 24 hours of data (plus header)

def getResponse(url):
    # Send a GET request without authentication
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        temperature = data["temperature"]
        humidity = data["humidity"]
        pressure = data["pressure"]

        csv_line = f"{temperature:.2f},{humidity:.2f},{pressure:.2f}"
        print(csv_line)
        return csv_line
    else:
            print("Failed to retrieve data from the server.")
            return None

def clear_data_lines_in_csv(path):
    try:
        with open(path, 'r') as csvfile:
            lines = csvfile.readlines()
            if len(lines) >= FILE_LIMIT:
                with open(path, 'w', newline='') as csvfile:
                    csvfile.truncate(0)
    except Exception as e:
        print(f'Error clearing data lines in CSV: {e}')

def csv_file_exists(path):
    try:
        with open(path, 'r') as csvfile:
            return csvfile.read().strip() != ''
    except FileNotFoundError:
        return False
    
def writeToFile(row):

    file_path = os.path.join(OUTPUT_DIR, "log.txt")
    
    if csv_file_exists(file_path):
        clear_data_lines_in_csv(file_path)
    else:
        print("creating log file")

    try:
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(["#Temperature, #Humidity, #Pressure"])  # Write header if file is empty
            writer.writerow(row.split(','))
    except Exception as e:
        print(f'Error writing to log file: {e}')

if __name__ == "__main__":
    result = getResponse(SERVER)
    if result:
        writeToFile(result)
