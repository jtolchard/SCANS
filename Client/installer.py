"""Installer for SCANS NMR Monitoring
Installer does not take any arguments, should be run with: "python3 installer.py"
Only requirements are a correctly editted clientparams.py file in the same 
directory as installer.py. The paths and log files named in this file should not
be changed. The output of the installer will be a ./bin folder containing scripts
that are correctly configured to load and monitor the log files on your system.
"""

__author__ = "James Tolchard"
__license__ = "GPLV3"
__version__ = "0.5"
__maintainer__ = "James Tolchard"
__email__ = "james.tolchard@univ-lyon1.fr"
__status__ = "Development"

import clientparams
import os.path
import sys
import glob
import subprocess
from subprocess import PIPE
from pathlib import Path

bin_path = './bin/'
output_path = '/Users/James/Code/NMR/SCANS/logging'
log_name = 'demo_log.txt'
param_path = clientparams.__file__

def run_command(command):
    popen = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    popen.wait(500) # wait a little for docker to complete
    return popen

def pathbuilder():

    print(f"Reading parameter file {param_path}")
    # Read the config file and extract the "used" parameter dictionaries
    with open(param_path) as f:
        exec(f.read())
        metric_list = [params for name, params in locals().items() if isinstance(params, dict) and 'use' in params and params['use']]

    # For each valid dictionary
    path = ""
    ks = ""
    for metric in metric_list:
        # check its logfile exists (if not - print out the failures)
        if not os.path.exists(metric['path']):
            print(f"{metric['path']} not found!")
            # If any logfile is missing, set a variable to abort the installer
            ks = True
        #  Otherwise build a formatted string docker can use for mounting this files    
        else:
            x = (f" -v {metric['path']}:/root/scans/logs/{metric['name']}.log")
            path += x
    # If you caught a missing file - exit the installer
    if ks:
        print(f"Check paths are set correctly in {param_path}")
        sys.exit(2)
    return path

# Generate a path list for use with docker scripts
path = pathbuilder()

# Unpack the bundled docker image
print("Unpacking docker image")
command = ["docker", "load", "-i", "docker/client.dkrimg"]
run_command(command)

# Wipe script if they already exist
if os.path.exists(os.path.join(bin_path, "scans_start")):
    print("Clearing existing scripts")
    files = glob.glob(os.path.join(bin_path, "*"))
    for f in files:
            os.remove(f)

# Build Scripts
cmd = f"scans /usr/bin/python3 scraper.py"
output = f"-v {output_path}:/root/scans/logs"
timesync = f"-v /etc/localtime:/etc/localtime:ro"
start_cmd = (f"docker run --name scans -e PYTHONUNBUFFERED=1 -d {timesync} {path} {output} {cmd} --output-file ./logs/{log_name}")
rebuild_cmd = (f"docker run --name scans_rebuild -e PYTHONUNBUFFERED=1 -d {timesync} {path} {output} {cmd} --rebuild --output-file ./logs/{log_name}")
build_run_cmd = (f"docker run --name scans_w_rebuild -e PYTHONUNBUFFERED=1 -d {timesync} {path} {output} {cmd} --rebuild-restart --output-file ./logs/{log_name}")
stop_cmd = ("docker rm -f scans 2>/dev/null; docker rm -f scans_w_rebuild 2>/dev/null; echo 'scans stopped'")
status_cmd = ("docker logs scans")

# Write scripts
print("Writing executable scripts")
# Start
f = open(os.path.join(bin_path, "scans_start"),"w+")
f.write(start_cmd)
f.close()
# rebuild
f = open(os.path.join(bin_path, "scans_rebuild"),"w+")
f.write(rebuild_cmd)
f.close()
# Build and start
f = open(os.path.join(bin_path, "scans_build+start"),"w+")
f.write(build_run_cmd)
f.close()
# Stop
f = open(os.path.join(bin_path, "scans_stop"),"w+")
f.write(stop_cmd)
f.close()
# Status
f = open(os.path.join(bin_path, "scans_status"),"w+")
f.write(status_cmd)
f.close()

# Make scripts executable
files = glob.glob(os.path.join(bin_path, "*"))
for f in files:
    os.chmod(f, 0o744)