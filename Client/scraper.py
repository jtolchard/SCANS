####
#### VERSION 0.4
####
import argparse
import csv
import sys
import time
import datetime
import clientparams
import os.path

param_path = clientparams.__file__
system_name = clientparams.system_name

def get_metrics(metric_list, rebuild_metric_db):
    """
    Retrieves metrics stored as dictionaries in clientparams.

    Args:
        metric_list (list): A list of dictionaries containing information about the metrics.
        rebuild_metric_db (bool): Whether to rebuild the metric database or not.

    Returns:
        A list of dictionaries containing the metric data.
    """

    metrics = []
    #Under typical use, we only consider the last lines of the logfiles
    if not rebuild_metric_db:
        for metric in metric_list:
            metric_logfile = metric['dockerpath']
            if os.path.exists(metric_logfile) and os.path.getsize(metric_logfile) > 0:
                with open(metric_logfile, 'r', encoding='utf-8') as logfile:
                    csv_reader = csv.reader(logfile, delimiter=metric['delim'])
                    last_row = list(csv_reader)[-1]
                    if last_row:
                        metric = {"name": metric['name'], "date": last_row[metric['datestamp_position']], "value": last_row[metric['datavalue_position']]+metric['units']}

                    # This works, but bloat the file. For now - removed
                    #else:
                    #    metric = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": f'error, log file empty. Check contents of {metric_logfile} defined in clientparams.py'}
            #This works, but bloat the file. For now - removed
            #else:
            #    metric = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": f'error accessing log file {metric_logfile}. Check path in clientparams.py'}
            metrics.append(metric)
        return metrics

    #Otherise, create a list of all datapoints for each metric from their log file
    else:
        for metric in metric_list:
            metric_logfile = metric['dockerpath']
            if os.path.exists(metric_logfile) and os.path.getsize(metric_logfile) > 0:
                with open(metric_logfile, 'r', encoding='utf-8') as logfile:
                    csv_reader = csv.reader(logfile, delimiter=metric['delim'])
                    # Bump csv_reader along +1 to skip header
                    next(csv_reader)
                    for row in csv_reader:
                        if row:
                            metric_row = {"name": metric['name'], "date": row[metric['datestamp_position']], "value": row[metric['datavalue_position']]+metric['units']}
                            metrics.append(metric_row)
            else:
                metric_row = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": f'error accessing log file {metric_logfile}. Check path in clientparams.py'}
                metrics.append(metric_row)
        return metrics
        
def build_output(output_file, rebuild_metric_db):

    # If outputfile already exist, create it
    if not os.path.exists(output_file):
        open(output_file, 'a').close()
    
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

def run_monitoring(freq):
    while(True):
        build_output(output_file, False)
        time.sleep(freq)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process metrics data')
    parser.add_argument('--rebuild', action='store_true', help='rebuild metric database from full logfiles', default=False)
    parser.add_argument('--rebuild-restart', action='store_true', help='rebuild metric database from full logfiles then continue monitoring', default=False)
    parser.add_argument("--output-file", help="path to output file", default="output.txt")
    parser.add_argument("--scan-frequency", help="number of seconds between rechecking logfiles", default=60)

    args = parser.parse_args()
    output_file = args.output_file
    rebuild_metric_db = args.rebuild
    rebuild_restart = args.rebuild_restart
    freq = args.scan_frequency

#@runtime
#Throwing an error with incompatible arguments
if rebuild_metric_db and rebuild_restart:
    print("rebuild and rebuild-restart are mutually exclusive")
    sys.exit(2)
# Running a rebuild and stopping
if rebuild_metric_db:
    print(f"Aggregating logs and exporting to: {output_file}")
    build_output(output_file, rebuild_metric_db)
    sys.exit(0)
# Build a complete log then start monitoring
if rebuild_restart:
    build_output(output_file, True)
    run_monitoring(freq)
# Build a complete log then start monitoring
if not rebuild_metric_db and not rebuild_restart:
    run_monitoring(freq)