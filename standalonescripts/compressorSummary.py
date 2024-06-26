import time
import datetime
import calendar
import requests

def query_prometheus(prometheus_url, query, params):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.get(prometheus_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: Unable to fetch data from Prometheus. Status code: {response.status_code}")
        print("Response content:")
        print(response.content)
        return None

def last_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    return (last_month.year,last_month.month)

if __name__ == "__main__":
    # Replace this URL with the actual URL of your Prometheus server.
    prometheus_url = 'http://{SERVER_IP}:9091/api/v1/query_range'
    # Calculate the timestamp for the current time
    current_time = int(time.time())

    lastMonth = last_month()
    lastMonthDays = calendar.monthrange(lastMonth[0], lastMonth[1])[1]

    # Calculate the timestamp for 24 hours ago
    start_time = current_time - (lastMonthDays * 24 * 60 * 60)

    # Construct the PromQL query to retrieve data for the metric "output_pressure"
    # within the last 24 hours across all jobs and instances.
    prometheus_query = f'output_pressure{{}}'

    # Create the parameters for the query range
    params = {
        'query': prometheus_query,
        'start': start_time,
        'end': current_time,
        'step': 300,  # Specify the step interval in seconds (e.g., 15 seconds)
    }

    # Call the function to query Prometheus
    data = query_prometheus(prometheus_url, prometheus_query, params)

    # Process the data if it's available
    if data:
        # The 'data' dictionary will contain the Prometheus query result.
        # You can access the actual values using data['data']['result'].

        # Example: Print the retrieved data
        for result in data['data']['result']:
            print(result['metric'], result['values'])
    else:
        print("No data returned from Prometheus.")

    
