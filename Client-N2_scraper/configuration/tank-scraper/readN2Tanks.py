import yaml
import json
import time
import csv
import requests
import os
from datetime import datetime, timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CONFIG_FILE = "/app/config.yml"
OUTPUT_DIR = "/app/logs"
FILE_LIMIT = 97 # i.e. keep 24 hours of data (plus header)

os.environ['TZ'] = 'Europe/Paris'
time.tzset()

# Read the configuration file and return the config dictionary.
def read_config():
    with open(CONFIG_FILE) as file:
        config = yaml.safe_load(file)
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
    print("Done.")

# Retrieve the AirLiquide session cookie for API access
def get_al_cookies(driver, wait, username, password):
    try:
        cookies_button1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.awe-popkies-bt_agree')))
        cookies_button1.click()
    except Exception as e:
        print("Error navigating initial cookies popup:", str(e))

    try:
        wait.until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.NAME, "pass"))).send_keys(password)
        driver.find_element(By.ID, "edit-submit").click()
    except Exception as e:
        print("Error performing login:", str(e))

    try:
        installation_button = wait.until(EC.presence_of_element_located((By.ID, 'my_installationss')))
        installation_button.click()
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, "Title")))
        driver.switch_to.window(driver.window_handles[1])
    except Exception as e:
        print("Error reaching dashboard:", str(e))

    try:
        cookies_button2 = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btnAcceptCookies')))
        cookies_button2.click()
    except Exception as e:
        print("Error navigating second cookies popup:", str(e))

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
            print("Error making API request:", str(e))
            if response is not None and response.status_code == 401 and retry < max_retries - 1:
                print(f"Retrying API request in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                break
    return None

# Handle the API response and write to CSV file.
def handle_tank_response(tank_name, api_data, nextDeliv):
    try:
        data = json.loads(api_data.text)
        value = data.get("Value")
        timestamp = data.get("Timestamp")
        is_in_alarm = data.get("IsInAlarm")

        if value is not None:
            print("Timestamp:", timestamp)
            print("Value:", value, "(%)")
            print("IsInAlarm:", is_in_alarm)
            print("Next Delivery:", nextDeliv)
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
                print("creating log file")
            
            try:
                with open(file_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if csvfile.tell() == 0:
                        writer.writerow(["#TimeStamp, #TankPercentage, #AlarmStatus, #NextDelivery"])  # Write header if file is empty
                    writer.writerow(row)
            except Exception as e:
                print(f'Error writing to log file: {e}')

        else:
            print("API response empty.")
    except ValueError as e:
        print("Error parsing API response:", str(e))
    except Exception as e:
        print("An unexpected error occurred:", str(e))


#Handle the API response and write to CSV file.
def handle_spi_response(name, pres_response, flow_response):
    try:
        pres_data = json.loads(pres_response.text)
        flow_data = json.loads(flow_response.text)
        
        spi_pres = ''
        spi_flow = ''
        spi_time = ''
        spi_pres = pres_data.get("Value")
        spi_flow = flow_data.get("Value")
        spi_time = flow_data.get("Timestamp")

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
                    writer.writerow(["#TimeStamp, #SPIpressure, #SPIflow"])  # Write header if file is empty
                writer.writerow(row)
        except Exception as e:
            print(f'Error writing to log file: {e}')

    except ValueError as e:
        print("Error parsing API 3/4 response:", str(e))
    except Exception as e:
        print("An unexpected error occurred:", str(e))


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

def main():
    config = read_config()
    username = config["Credentials"]["Username"]
    password = config["Credentials"]["Password"]
    url = config["Credentials"]["loginURL"]
    tanks = config["ALTanks"]["tanks"]
    spis = config["SPIs"]

    driver = configure_driver()
    wait = WebDriverWait(driver, 30)

    driver.get(url)
    cookies = get_al_cookies(driver, wait, username, password)

    cookies = {
        "cookies": cookies
    }

    # Create some friendly date strings
    now = datetime.now()
    yesterday = (datetime.now() - timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
    oneweek = (datetime.now() + timedelta(days=7)).replace(hour=1, minute=0, second=0, microsecond=0)

    now_string = now.strftime("%Y-%m-%d %H:%M:%S")
    yesterday_string = yesterday.strftime('%Y-%m-%d %H:%M:%S')
    oneweek_string = oneweek.strftime('%Y-%m-%d %H:%M:%S')

    for tank in tanks:

        api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+tank['tankID']+"/currentlevel"
        response1 = make_api_request(api_url, cookies)
        if response1:
            print("API request successful ("+now_string+")")

            api_url2 = "https://myinstallations.airliquide.com/france/server/api/v2/installation/"+tank['delID']+"/deliveries?startDate="+yesterday_string+"Z&endDate="+oneweek_string+"Z&isUtc=true"
            response2 = make_api_request(api_url2, cookies)

            desired_status = "Planned"
            delDate = "0"

            if response2 is not None:
                for item in json.loads(response2.text):
                    if item["Status"] == desired_status:
                        date_string = item["DeliveryDate"]
                        tidyDate = date_string.split(".")[0]
                        datetime_obj = datetime.strptime(tidyDate, "%Y-%m-%dT%H:%M:%S")
                        delDate = datetime_obj.timestamp()
                        break

            handle_tank_response(tank['name'], response1, delDate)

    for spi in spis:
        spi_pres_api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+spi['ID']+"/currentpressure"
        spi_flow_api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+spi['ID']+"/flowmeter/currentvalue"
        
        pres_response = make_api_request(spi_pres_api_url, cookies)
        flow_response = make_api_request(spi_flow_api_url, cookies)

        handle_spi_response(spi['name'], pres_response, flow_response)

    close_browser(driver)

if __name__ == "__main__":
    main()
