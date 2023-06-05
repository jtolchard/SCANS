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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CONFIG_FILE = "/app/config.yml"

OUTPUT_DIR = "/app/logs"

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
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    #return webdriver.Chrome(options=chrome_options)

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
def handle_api_response(api_data, nextDeliv, tank_name, inc):
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

            # Prepare the data row
            row = [timestamp, value, is_in_alarm, nextDeliv]

            # Replace whitespace with underscore in tank name
            tank_name = tank_name.replace(" ", "_")

            # Prepare the file path
            file_path = os.path.join(OUTPUT_DIR, inc, "log.txt")

            # Write data to CSV file
            with open(file_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(["#TimeStamp, #TankPercentage, #AlarmStatus, #NextDelivery"])  # Write header if file is empty
                writer.writerow(row)

        else:
            print("API response empty.")
    except ValueError as e:
        print("Error parsing API response:", str(e))
    except Exception as e:
        print("An unexpected error occurred:", str(e))

def main():
    config = read_config()
    username = config["Credentials"]["Username"]
    password = config["Credentials"]["Password"]
    url = config["Credentials"]["loginURL"]
    tanks = config["ALTanks"]["tanks"]

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

    # Create an int to help distinguish the log file dirs
    inc = 0

    for tank in tanks:
        
        inc += 1

        api_url = "https://myinstallations.airliquide.com/france/server/api/v2/tank/"+tank['tankID']+"/currentlevel"
        response1 = make_api_request(api_url, cookies)
        if response1:
            print("API request successful ("+now_string+")")

            api_url2 = "https://myinstallations.airliquide.com/france/server/api/v2/installation/"+tank['delID']+"/deliveries?startDate="+yesterday_string+"Z&endDate="+oneweek_string+"Z&isUtc=true"
            response2 = make_api_request(api_url2, cookies)

            desired_status = "Planned"

            for item in json.loads(response2.text):
                  if item["Status"] == desired_status:
                    datetime_obj = datetime.strptime(item["DeliveryDate"], "%Y-%m-%dT%H:%M:%S.%f")
                    delDate = datetime_obj.strftime("%Y-%m-%d %H:%M")
                    break
            else:
                delDate = "Unknown"

            print("Delivery date is: "+delDate)
            
            handle_api_response(response1, delDate, tank['name'], str(inc))

    close_browser(driver)

if __name__ == "__main__":
    main()
