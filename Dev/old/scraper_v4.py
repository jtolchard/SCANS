import argparse
import csv
import pathlib
import clientparams
from datetime import datetime
from collections import defaultdict

param_path = clientparams.__file__
#system_name = clientparams.system_name

def get_metrics(metric_list, rebuild_metric_db=False):
    metrics = []

    if rebuild_metric_db:
        for metric in metric_list:
            try:
                with open(metric['path'], 'r') as f:
                    reader = csv.reader(f, delimiter=metric['delim'])
                    next(reader)  # skip header
                    for row in reader:
                        name = metric['name']
                        date = row[metric['datestamp_position']]
                        value = row[metric['datavalue_position']] + metric['units']
                        metrics.append({'name': name, 'date': date, 'value': value})
            except FileNotFoundError:
                metrics.append({'name': metric['name'], "date":datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'error': f'error accessing log file {metric["path"]}. Check path in clientparams.py'})
    else:
        for metric in metric_list:
            try:
                with open(metric['path'], 'r') as f:
                    reader = csv.reader(f, delimiter=metric['delim'])
                    last_row = list(reader)[-1]
                    if last_row:
                        name = metric['name']
                        date = last_row[metric['datestamp_position']]
                        value = last_row[metric['datavalue_position']] + metric['units']
                        metrics.append({'name': name, 'date': date, 'value': value})
                    else:
                        metrics.append({'name': metric['name'], 'error': f'error, log file {metric["path"]} empty. Check contents of logfile defined in clientparams.py'})
            except FileNotFoundError:
                metrics.append({'name': metric['name'], 'date':datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'error': f'error accessing log file {metric["path"]}. Check path in clientparams.py'})

    # group the data by metric name
    grouped_metrics = defaultdict(list)
    for metric in metrics:
        name = metric['name']
        grouped_metrics[name].append(metric)

    # sort the data by date within each metric group
    for name, data in grouped_metrics.items():
        grouped_metrics[name] = sorted(data, key=lambda x: x['date'])

    # flatten the dictionary back into a list
    flattened_metrics = [metric for metrics in grouped_metrics.values() for metric in metrics]

    return flattened_metrics

def test_output(rebuild_metric_db=False):

    # If outputfile already exist, create it
    if not pathlib.Path(output_file).exists():
        pathlib.Path(output_file).touch()

    # Generate a list of the requested metrics
    with open(param_path) as f:
        exec(f.read())
    metric_list = [params for name, params in locals().items() if isinstance(params, dict) and 'use' in params and params['use']]

    #Generate a dictionary containing the requested metric outputs
    metric_data = get_metrics(metric_list, rebuild_metric_db)
    
    #Create a variable to help read existing data
    existing_data = set()

    # Create a list of name:date pairs to avoid duplicating data points 
    # Open the output file in read mode and read all existing lines into memory
    with open(output_file, 'r') as f:
        for line in f:
            # Strip any whitespace from the line and convert it to a dictionary using eval()
            metric = eval(line.strip())
            # Create a tuple of the name and age keys for this dictionary
            key = (metric['name'], metric['date'])
            # Add the key tuple to the set of keys written
            existing_data.add(key)

    #Write the new dictionary outputs to a file (one line per metric) as long as they haven't been seen before
    with open(output_file, 'a') as f:
        for metric in metric_data:
            #Create a tuple defining a unique data point
            key = (metric['name'], metric['date'])

            if key not in existing_data:
                f.write(str(metric) + '\n')
    #print(existing_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process metrics data')
    parser.add_argument('--rebuild', action='store_true', help='rebuild metric database from full logfiles')
    parser.add_argument("--output-file", help="path to output file", default="output.txt")

    args = parser.parse_args()
    output_file = args.output_file

    #@runtime
    test_output(rebuild_metric_db=args.rebuild)