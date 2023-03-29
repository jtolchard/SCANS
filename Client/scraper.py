"""Logfile scraper for SCANS NMR Monitoring
This file should not be altered. It is used within the docker container for 
parsing the logs defined in clientparams.py. Under normal operation, scraper.py
should not be run manually. The correctly configured commands will be generated
by installer.py and written to ./bin.

The possible arguments are:
    --rebuild = creates a one-off logfile aggregated from the logs defined in
                clientparams.py (should not be used with --rebuild-restart)

    --rebuild = creates a logfile aggregated from the logs defined in
                clientparams.py and continues active monitoring of these files.
                (should not be used with --rebuild-restart)

    --output-file = defines the name of the output logfile

    --scan-frequency = How regularly the logs should be updated. The default 
                       value is 60 seconds.
"""

__author__ = "James Tolchard"
__license__ = "GPLV3"
__version__ = "0.5"
__maintainer__ = "James Tolchard"
__email__ = "james.tolchard@univ-lyon1.fr"
__status__ = "Development"

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
                        metrics.append(metric)
            elif os.path.exists(metric_logfile) and os.path.getsize(metric_logfile) == 0:
                print(f"Warning, {metric_logfile} is empty")     
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
            
            elif os.path.exists(metric_logfile) and os.path.getsize(metric_logfile) == 0:
                print(f"Warning, {metric_logfile} is empty")
            #else:
                #metric_row = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": f'error reading log file {metric_logfile}. Check file is path in clientparams.py'}
                #metrics.append(metric_row)
        return metrics
        
def build_output(output_file, rebuild_metric_db):

    # If outputfile doesn't exist, create it
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
    print(f"Running in monitoring-mode on {system_name}. Scanning every {freq} seconds.")
    while(True):
        build_output(output_file, False)
        print("Scan run at "+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
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