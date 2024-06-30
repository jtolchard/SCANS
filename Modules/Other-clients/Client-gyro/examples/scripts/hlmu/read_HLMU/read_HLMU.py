import requests
from bs4 import BeautifulSoup
import csv
import os

# IP address and URL of the webpage
ip_address = "10.236.99.8"
url = f"http://{ip_address}/control.html"
OUTPUT_DIR = "/app/logs"

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all tables with the class "body"
    tables = soup.find_all("table", class_="body")

    # Check if at least two tables with the class "body" exist
    if len(tables) >= 2:
        # Get the second table with the class "body"
        table = tables[1]


        # Prepare the file path
        file_path = os.path.join(OUTPUT_DIR, "log.txt")

        # Extract data from the table and output to a file
        with open(file_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Check if the file is empty
            if csvfile.tell() == 0:
                # Write header if file is empty
                writer.writerow(["HeliumLevel_%", "NitrogenLevel_%"])

            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 3:
                    helium_lvl = cells[2].text.strip()[:-2]
                    nitrogen_lvl = cells[3].text.strip()[:-2]
                    csv_row = [helium_lvl, nitrogen_lvl]
                    writer.writerow(csv_row)
                #else:
                    #print("Insufficient number of columns in the table row.")
    else:
        print("Failed to retrieve the webpage.")
else:
    print("Request to the webpage failed.")
