import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import csv
from requests.auth import HTTPBasicAuth

## This is specifically for a Network connected SOCOMEC UPS system.
## Probably won't be of direct use, but an example of how to scrape values off a web page to a log file

address_dict = {'server-ups':
                {'status': {'url': 'http://192.168.X.X/cgi.ssp?a=000', 'tag': 't1', 'table':'n'},
                'battery': {'url': 'http://192.168.X.X/cgi.ssp?a=004', 'tag': 't3','table':'y', 'cell_location': (1, 1)}}
            }

USERNAME = "admin"
PASSWORD = "public"
OUTPUT_DIR = "/app/logs"
FILE_LIMIT = 289 # i.e. keep 24 hours of data (plus header)

def getResponse(url, tag, tabled, cell_location=None):
    # Send a GET request with authentication
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find the element with the specified tag
        target = soup.find(class_=tag)
        
        if target:
            if tabled == 'y':
                table = soup.find_all('table')
                df = pd.read_html(str(table))[1]
                text = df.iloc[cell_location[0], cell_location[1]]
                return text.strip()
            else:
                text = target.get_text()
                return text.strip()
        else:
            print("Element with class '{}' not found on the page.".format(tag))
            return None
    else:
        print("Failed to fetch the page. Status code:", response.status_code)
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
                writer.writerow(["#Status, #Battery%"])  # Write header if file is empty
            writer.writerow(row)
    except Exception as e:
        print(f'Error writing to log file: {e}')

if __name__ == "__main__":
    row = []
    for ups, properties in address_dict.items():
        row.append(ups)
        for page, props in properties.items():
            result = getResponse(props['url'], props['tag'], props['table'], props.get('cell_location'))
            if result:
                print("ups: {} = {}".format(page, result))
                row.append(result)

        writeToFile(row)
