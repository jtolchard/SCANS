import csv
import datetime
import clientparams
import pathlib

def get_metrics(metric_list, rebuild_metric_db=False):
    metrics = []

    for metric in metric_list:
        if not pathlib.Path(metric['path']).exists():
            metric = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": 'error accessing log file. Check path in clientparams.py'}
            metrics.append(metric)
            continue

        if rebuild_metric_db:
            with open(metric['path'], 'r') as logfile:
                csv_reader = csv.reader(logfile, delimiter=metric['delim'])
                next(csv_reader) # Skip header
                for row in csv_reader:
                    if row:
                        metric_row = {"name": metric['name'], "date": row[metric['datestamp_position']], "value": row[metric['datavalue_position']]+metric['units']}
                        metrics.append(metric_row)

        else:
            with open(metric['path'], 'r') as logfile:
                size = pathlib.Path(metric['path']).stat().st_size
                logfile.seek(size - 2) # Seek to second last character
                while logfile.read(1) != '\n': # Find last newline character
                    logfile.seek(-2, 1) # Seek back one character
                last_row = list(csv.reader(logfile, delimiter=metric['delim']))[-1]
                if last_row:
                    metric = {"name": metric['name'], "date": last_row[metric['datestamp_position']], "value": last_row[metric['datavalue_position']]+metric['units']}
                else:
                    metric = {"name":metric['name'],  "date":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "error": 'error, log file empty. Check contents of logfile defined in clientparams.py'}
                metrics.append(metric)

    return metrics

def test_output(rebuild_metric_db=False):
    output_filename = 'output.txt'

    if not pathlib.Path(output_filename).exists():
        pathlib.Path(output_filename).touch()

    with open(clientparams.__file__) as f:
        exec(f.read())
    metric_list = [params for name, params in locals().items() if isinstance(params, dict) and 'use' in params and params['use']]
    metric_data = get_metrics(metric_list, rebuild_metric_db)

    existing_data = {(metric['name'], metric['date']) for line in open(output_filename) for metric in [eval(line.strip())]}

    with open(output_filename, 'a') as f:
        for metric in metric_data:
            key = (metric['name'], metric['date'])
            if key not in existing_data:
                f.write(str(metric) + '\n')
                existing_data.add(key)