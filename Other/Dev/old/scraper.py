import csv
import datetime
import clientparams
from os import path

param_path = clientparams.__file__
system_name = clientparams.system_name
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

def get_metric_list(filename):

    # read the parameter file
    with open(filename) as f:
        exec(f.read())
    
    # create a list of dictionaries with a "Use" flag set to "True"
    param_list = []
    for name, params in locals().items():
        if isinstance(params, dict) and 'use' in params and params['use']:
            param_list.append(params)
    
    return param_list

def get_metrics(metric_list):
    metrics = []
    for metric in metric_list:
        if path.exists(metric['path']):
            with open(metric['path'], 'r') as logfile:
                csv_reader = csv.reader(logfile, delimiter=metric['delim'])
                last_row = list(csv_reader)[-1]
                if last_row:
                    metric = {"name": metric['name'], "date": last_row[metric['datestamp_position']], "value": last_row[metric['datavalue_position']]+metric['units']}

                else:
                    metric = {"name":metric['name'],  "date":timestamp, "error": 'error, log file empty. Check contents of logfile defined in clientparams.py'}
        else:
            metric = {"name":metric['name'],  "date":timestamp, "error": 'error accessing log file. Check path in clientparams.py'}
        
        metrics.append(metric)

    return metrics

def test_output(rebuild_metric_db=False):

    # Define an output file
    output_filename = 'output.txt'
    # If it doesn't already exist, create it
    if not path.exists(output_filename):
        open(output_filename, 'a').close()
    
    #Generate a list of the requested metrics
    metric_list = get_metric_list(param_path)
    #Generate a dictionary containing the requested metric outputs
    metric_data = get_metrics(metric_list)   
    
    #Create a variable to help read existing data
    existing_data = set()

    # Create a list of name:date pairs to avoid duplicating data points 
    # Open the output file in read mode and read all existing lines into memory
    with open(output_filename, 'r') as f:
        for line in f:
            # Strip any whitespace from the line and convert it to a dictionary using eval()
            metric = eval(line.strip())
            # Create a tuple of the name and age keys for this dictionary
            key = (metric['name'], metric['date'])
            # Add the key tuple to the set of keys written
            existing_data.add(key)

    #Write the new dictionary outputs to a file (one line per metric) as long as they haven't been seen before
    with open(output_filename, 'a') as f:
        for metric in metric_data:
            #Create a tuple defining a unique data point
            key = (metric['name'], metric['date'])

            if key not in existing_data:
                f.write(str(metric) + '\n')
    #print(existing_data)



test_output(rebuild_metric_db=True)
#metric_list = get_metric_list(param_path)
#metric_data = get_metrics(metric_list)
#print(metric_data)


