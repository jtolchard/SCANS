import os
import time
import logging
import json
import csv
import argparse
from datetime import datetime, timedelta
import yaml
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

########################## VARIABLES #########################
CONFIG_FILE = "/app/config.yml"
OUTPUT_DIR = "/app/logs"
TANK_FILE_HEADER = ["TimeStamp", "TankPercentage", "AlarmStatus", "NextDelivery"]
SPI_FILE_HEADER = ["TimeStamp", "SPIpressure", "SPIflow"]
FILE_LIMIT = 145 # i.e. keep 24 hours of data (plus header)
TIMEZONE = "Europe/Paris"
##############################################################

os.environ['TZ'] = TIMEZONE
time.tzset()

# Argparse block
def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to retrieve AirLiquide Logs and store data to csv logfiles.")
    parser.add_argument("--log-stdout", action="store_true", help="Enable logging messages to STDOUT")
    return parser.parse_args()

# Read the configuration file and return the config dictionary.
def read_config(file_path):
    with open(file_path) as file:
        config = yaml.safe_load(file)
        logging.info("Reading config file.")
    return config

# Configure and return the Chrome WebDriver.
def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Close the browser and quit the WebDriver.
def close_browser(driver):
    driver.quit()
    logging.info("Browser closed.")

# Retrieve the AirLiquide session cookie for API access
def get_al_cookies(driver, wait, username, password):
    try:
        cookies_button1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.awe-popkies-bt_agree')))
        cookies_button1.click()
    except Exception as e:
        logging.error(f"Error navigating initial cookies popup: {e}")

    try:
        wait.until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.NAME, "pass"))).send_keys(password)
        driver.find_element(By.ID, "edit-submit").click()
    except Exception as e:
        logging.error(f"Error performing login: {e}")

    try:
        installation_button = wait.until(EC.presence_of_element_located((By.ID, 'my_installationss')))
        installation_button.click()
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, "Title")))
        driver.switch_to.window(driver.window_handles[1])
    except Exception as e:
        logging.error(f"Error reaching dashboard: {e}")

    try:
        cookies_button2 = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btnAcceptCookies')))
        cookies_button2.click()
    except Exception as e:
        logging.error(f"Error navigating second cookies popup: {e}")

    cookies_json = driver.get_cookies()
    cookies_str = ''.join(map(lambda c: '%s=%s; ' % (c['name'], c['value']), cookies_json))
    return cookies_str

def make_api_request(url, cookies, max_retries=3, retry_delay=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
    }

    response = None  # Initialize the response variable
    for retry in range(max_retries):
        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=2)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error making API request: {e}")
            if response is not None and response.status_code == 401 and retry < max_retries - 1:
                print(f"Retrying API request in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                break
    return None

# Handle the API response and write to CSV file.
def handle_tank_response(tank_name, api_data, nextDeliv):
    try:
        value = api_data.get("Value")
        timestamp = api_data.get("Timestamp")
        is_in_alarm = api_data.get("IsInAlarm")

        if value is not None:
            print(f"Tank: {tank_name}")
            print(f"Timestamp: {timestamp}")
            print(f"Value: {value}")
            print(f"IsInAlarm: {is_in_alarm}")
            print(f"Next Delivery: {nextDeliv}")
            print("---")

            # Replace whitespace with underscore in tank name
            tank_name = tank_name.replace(" ", "_")

            # Prepare the data row
            row = [tank_name, timestamp, value, is_in_alarm, nextDeliv]

            # Prepare the file path
            file_path = os.path.join(OUTPUT_DIR, "tanks", "log.txt")

            if csv_file_exists(file_path):
                clear_data_lines_in_csv(file_path)
            else:
                logging.info("creating log file")
            
            try:
                with open(file_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if csvfile.tell() == 0:
                        # Write header if file is empty
                        writer.writerow(TANK_FILE_HEADER)
                    writer.writerow(row)
            except Exception as e:
                logging.error(f"Error writing to log file: {e}")

        else:
            print("API response empty.")
    except ValueError as e:
        print(f"Error parsing API response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


#Handle the API response and write to CSV file.
def handle_spi_response(name, pres_response, flow_response):
    try:
        pres_data = json.loads(pres_response.text)
        flow_data = json.loads(flow_response.text)
        
        if pres_data.get("Value") is not None:
            spi_pres = pres_data.get("Value")
        else:
            spi_pres = ''

        if flow_data.get("Value") is not None:
            spi_flow = flow_data.get("Value")
            spi_time = flow_data.get("Timestamp")
        else:
            spi_flow = ''
            spi_time = ''
            
        print(f"SPI: {name}")    
        print(f"Timestamp: {spi_time}")
        print(f"Pressure: {spi_pres} bar")
        print(f"Flow: {spi_flow} m3/hr")
        print("---")

        # Prepare the data row
        row = [name, spi_time, spi_pres, spi_flow]

        # Prepare the file path
        file_path = os.path.join(OUTPUT_DIR, "spi", "log.txt")

        if csv_file_exists(file_path):
            clear_data_lines_in_csv(file_path)
        else:
            print("creating log file")
            
        try:
            with open(file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(SPI_FILE_HEADER)  # Write header if file is empty
                writer.writerow(row)
        except Exception as e:
            logging.error(f"Error writing to log file: {e}")

    except ValueError as e:
        logging.error(f"Error parsing API 3/4 response: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def clear_data_lines_in_csv(path):
    try:
        with open(path, 'r') as csvfile:
            lines = csvfile.readlines()
            if len(lines) >= FILE_LIMIT:
                with open(path, 'w', newline='') as csvfile:
                    csvfile.truncate(0)
    except Exception as e:
        logging.error(f"Error clearing data lines in CSV: {e}")

def csv_file_exists(path):
    try:
        with open(path, 'r') as csvfile:
            return csvfile.read().strip() != ''
    except FileNotFoundError:
        return False

# Function to create some standard dates relative to now
def get_relativedates():
    now = datetime.now()
    yesterday = (now - timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
    tomorrow = (now + timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
    oneweek = (now + timedelta(days=7)).replace(hour=1, minute=0, second=0, microsecond=0)
    return now, yesterday, tomorrow, oneweek

def main():
    
    args = parse_arguments()
    if args.log_stdout:
        logging.basicConfig(level=logging.INFO)

    # Retrieve API config, login credentials, and installation details
    config = read_config(CONFIG_FILE)
    username, password, url = config["Credentials"]["Username"], config["Credentials"]["Password"], config["Credentials"]["loginURL"]
    tanks, spis = config["ALTanks"]["tanks"], config["SPIs"]
    
    # Create a webdriver and retrieve cookies 
    driver = configure_driver()
    wait = WebDriverWait(driver, 30)
    driver.get(url)
    cookies = get_al_cookies(driver, wait, username, password)
    cookies = {"cookies": cookies}

    # Set relative dates and formatted strings
    now, yesterday, tomorrow, oneweek = get_relativedates()
    now_string = now.strftime("%Y-%m-%d %H:%M:%S")
    yesterday_string = yesterday.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    tomorrow_string = tomorrow.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    oneweek_string = oneweek.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    for tank in tanks:
        
        #Get tank API data from top-page
        api_url1 = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+tank['tankID']+"/currentlevel"
        logging.info(f"API request 1 = {api_url1}")
        response1 = make_api_request(api_url1, cookies)
        
        if response1 is not None: 
            r1_json = json.loads(response1.text)
            r1_time = datetime.strptime(r1_json.get("Timestamp"), "%Y-%m-%dT%H:%M:%S")
            #Take the body of the response from the API response 1
            response = json.loads(response1.text)

            #Get tank API data from chart page
            api_url2 = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+tank['tankID']+"/level?startDate="+yesterday_string+"Z&endDate="+tomorrow_string+"Z&isUtc=true"
            logging.info(f"API request 2 = {api_url2}")
            response2 = make_api_request(api_url2, cookies)

            if response2 is not None: 
                r2_json = json.loads(response2.text)
                r2_time = datetime.strptime(r2_json[-1].get('LocalTime'), "%Y-%m-%dT%H:%M:%S")
            else:
                logging.error("API response 2 empty")

            # update the timestamp and value depending on the latest reading
            if r2_time > r1_time:
                logging.info("latest value = API2")
                response["Timestamp"] = r2_json[-1].get('LocalTime')
                response["Value"] = r2_json[-1].get('Value')
            else:
                logging.info("latest value = API1")          
        else:
            logging.error("API response 1 empty")
        
        if response1 and response2:
            print(f"API request successful @ {now_string}")
            print("---")
            api_url3 = "https://myinstallations.airliquide.com/france/server/api/v2/installation/"+tank['delID']+"/deliveries?startDate="+yesterday_string+"Z&endDate="+oneweek_string+"Z&isUtc=true"
            logging.info(f"API request 3 = {api_url3}")
            response3 = make_api_request(api_url3, cookies)

            desired_status = "Planned"
            delDate = "0"

            if response3 is not None:
                for item in json.loads(response3.text):
                    if item["Status"] == desired_status:
                        date_string = item["DeliveryDate"]
                        tidyDate = date_string.split(".")[0]
                        datetime_obj = datetime.strptime(tidyDate, "%Y-%m-%dT%H:%M:%S")
                        eval_date = datetime_obj.date()

                        # If the delivery date was in the past - discard it.
                        if (now.date() > eval_date):
                            delDate = "0"
                        else:
                            delDate = datetime_obj.timestamp()
                        break

            handle_tank_response(tank['name'], response, delDate)

    for spi in spis:
        spi_pres_api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+spi['ID']+"/currentpressure"
        spi_flow_api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+spi['ID']+"/flowmeter/currentvalue"
        
        pres_response = make_api_request(spi_pres_api_url, cookies)
        flow_response = make_api_request(spi_flow_api_url, cookies)

        handle_spi_response(spi['name'], pres_response, flow_response)

    close_browser(driver)

if __name__ == "__main__":  
    main()
