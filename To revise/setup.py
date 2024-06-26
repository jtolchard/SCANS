"""Setup script for SCANS NMR Monitoring
The SCANS installer does not take any arguments, and should be run, as root (or sudo)
with: "python3 installer.py"
The only requirements are that docker and docker-compose are correctly installed (i.e.
their executables are available in your path. The paths and log files named in
this file should not be changed. 

## NOT SURE YET
The output of the installer will be a ./bin folder containing scripts
that are correctly configured to load and monitor the log files on your system.
"""

## Boilerplate
__author__ = "James Tolchard"
__license__ = "GPLV3"
__version__ = "0.5"
__maintainer__ = "James Tolchard"
__email__ = "james.tolchard@univ-lyon1.fr"
__status__ = "Development"

## Imports
import subprocess
import os
import socket

## Core variables
dependencies = ['docker','docker-compose']
bin_path = './bin/'

# Print ASCII header
print('''
___________________________________
  ____   ____    _    _   _ ____  
 / ___| / ___|  / \  | \ | / ___| 
 \___ \| |     / _ \ |  \| \___ \ 
  ___) | |___ / ___ \| |\  |___) |
 |____/ \____/_/   \_\_| \_|____/ 
 
       SCANS CONTAINER SETUP 
___________________________________
''')

## Custom Functions

# Check for necessary packages
def check_package(package_name):
    return subprocess.call(["command", "-v", package_name], stdout=subprocess.PIPE) == 0

# Read and doublecheck user input to a custom question
def check_input(text):
    count = 0
    while count != 1:
        inp = input(text)
        chk = input(f"Is {inp} correct? (y/n): ")
        if chk == "y":
            return inp

# Obtain local IP address
def localip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error:
        return None

# Log types
def deflogdic():
    logdict = {
    "helium": "heliumlogcache.log",
    "nitrogen": "nitrogenlogcache.log",
    "field": "field.log",
    "shim": "rtshims.log",
    "events": "events.log",
    }
    return(logdict)
    

# Define monitoring elements
def log_build(log_path):
    logs = deflogdic()
    for key, value in logs.items():
        name = key
        file = value
        log_file = os.path.join(log_path, file)
        print(log_file)
        if os.path.isfile(log_file) is False:
            log_file = ""
            print(f"{name} log not found")
        else:
            print(f"{name} monitoring found!")
            logs[name] = log_file
    # Return a dictionary of existing log files
    return (logs)


## RUN MAIN
print("Please run this script as root (or sudo) privileges\n")

# Check for dependencies
for dependency in dependencies:
    if not check_package(dependency):
        print(f"{dependency} is not installed/accessible. Please install and check your PATH to proceed.")
        exit(1)

if not check_package("git"):
    print("git was not found within the system paths. It's installation is recommended to streamline deployment.")

# Ask user for type of installation
modules = [
    "Spectrometer Logging",
    "Server/RAID Logging",
    "Monitoring System & DBs"
]
# Print module selection
for i, module in enumerate(modules):
    print(f"{i + 1}. {module}")
print()

menu_entry_index = None
while menu_entry_index is None:
    try:
        menu_entry_index = int(input("Choice: ")) - 1
        if menu_entry_index < 0 or menu_entry_index >= len(modules):
            raise ValueError()
    except ValueError:
        print("Invalid response. Please enter a number corresponding to one of the above modules.")

# Setup for spectrometer logging container
if menu_entry_index == 0:
    print("Setting up Spectrometer Logging Module\n")
    # Ask user for spectrometer name
    spect_name = check_input("Choose a unique spectrometer name: ")

    # Check for MICS
    try:
        mics_status = subprocess.run(['systemctl is-active --quiet mics'], check = True)
        mics_enabled = subprocess.run(['systemctl is-enabled --quiet mics'], check = True)
    except:
        print("\nUnable to check MICS service status.")
        mics_status = 1

    # If MICS is running and enabled for startup.. 
    if mics_status == 0 and mics_enabled == 0:
        print(f"The Bruker MICS service is currently active and enabled at startup.")
        if os.path.isfile("/opt/Bruker/mics/logs/heliumlogcache.log"):
            print(f"MICS logs were found at /opt/Bruker/mics/logs/. These will be used for setup.")
            log_path = "/opt/Bruker/mics/logs/"
            logs = log_build(log_path)
        else:
            print(f"MICS logs were NOT found in their typical location.")
            log_path = check_input("Please provide the absolute path for your log files (i.e., /opt/logs): ")                  
            
            # If you provided a dud path, quit
            if os.path.isdir(log_path) is False:
                print(f"The provided path does not exist - please locate your log files and restart setup.")
                exit(1)

    # If MICS is running, but it isn't enabled at startup..
    elif mics_status == 0 and mics_enabled != 0:
        print(f"The Bruker MICS service is currently active but NOT enabled at startup.")
        chk = input("Would you like to enable MICS at startup? (y/n): ")  
        if chk == "y":
            if os.path.isfile("/opt/Bruker/mics/runmicsctrl"):
                os.system('sudo systemctl enable MICS/MICS_Service.service')
                os.system('sudo systemctl start MICS/MICS_Service.service')
                os.system('sudo systemctl daemon-reload')
                # Check everything went well
                mics_enabled = os.system('systemctl is-enabled --quiet mics')
                if mics_enabled == 0:
                    print("MICS enabled.")
                else:
                    print("Something went wrong.. please check MICS is enabled after setup.")
            else:
                print("MICS scripts were not found in the usual location, please check your setup.")
                print("MICS can be manually enabled in the future, but note - monitoring will fail if your machine reboots and MICS isn't manually restarted.")
        else:
            print("MICS can be manually enabled in the future, but note - monitoring will fail if your machine reboots and MICS isn't manually restarted.")

        if os.path.isfile("/opt/Bruker/mics/logs/heliumlogcache.log"):
            print(f"MICS logs were found at /opt/Bruker/mics/logs/. These will be used for setup.")
            log_path = "/opt/Bruker/mics/logs/"
            logs = log_build(log_path)
        else:
            print(f"MICS logs were NOT found in their typical location.")
            log_path = check_input("Please provide the absolute path for your log files (i.e., /opt/logs): ") 

            # If you provided a dud path, quit
            if os.path.isdir(log_path) is False:
                print(f"The provided path does not exist - please locate your log files and restart setup.")
                exit(1)

    # If MICS is not running
    elif mics_status == 1:
        print(f"MICS is not running.")
        print(f"You can check whether mics is setup by running 'mics' in TopSpin.")
        print("Please consult the README file for more information and how to enable it at boot time.\n")

        chk = input("Would you like to monitor non-MICS TopSpin logs? (y/n): ")  
        if chk == "y":
            log_path = check_input("Please provide the absolute path for your log files (i.e., /opt/logs): ") 
            # If you provided a dud path, quit
            if os.path.isdir(log_path) is False:
                print(f"The provided path does not exist - please locate your log files and restart setup.")
                exit(1)
        print("No problem. Monitoring will be limited to computer metrics.\n")  
        x = log_build(log_path)
        print(x)

#    # Define grok config file
#    # Build file path
#    grok_config_file = os.path.join("Client-spec", "configuration", "grok.yml")
#    # Read current config file
#    with open(grok_config_file, "r") as file:
#        file_contents = file.read()
#    updated_file_contents = file_contents.replace("$SPECT_NAME", spect_name)
#    # Write the spectrometer name to the grok file
#    with open(grok_config_file, "w") as file:
#        file.write(updated_file_contents)#3
#
#    # Build docker-compose config
#    # Build file path
#    dkrcomp_config_file = os.path.join("Client-spec", "docker-compose.yml")
#    # Read current docker-compose yml file
#    with open(dkrcomp_config_file, "r") as file:
#        file_contents = file.read()
#    updated_file_contents = file_contents.replace("$LOG_PATH:", log_path)
#    # Write the log file path to the docker-compose yml file
#    with open(dkrcomp_config_file, "w") as file:
#        file.write(updated_file_contents)


    # Build metrics block for grok
    #for 
    #    - type: gauge
    #  name: helium_level
    #  help: The helium level value as stored in the Bruker logs
    #  path: /opt/example/helium.log
    #  match: '%{TIMESTAMP_ISO8601:timestamp};%{NUMBER:helium}'
    #  value: '{{.helium}}'
    #  cumulative: false

    # Find local IP address and print out target line for user 
    ip_address = localip()
    if ip_address is not None:
        print(f"Done.\nParameters setup.")
        print(f"Ensure the docker-compose.yml file for your monitoring system(s) contains the new 'extra_hosts' line")
        print(f'- "{spect_name}:{ip_address}"')
    else:
        print(f"IP address not found, please try again when connected to the local network")
        exit(1)

# Setup for server logging container
elif menu_entry_index == 1:
    print("Setting up Server/RAID Logging module")
    # TODO: add code to set up server and RAID logging module

# Setup for monitoring container
elif menu_entry_index == 2:
    print("Setting up Monitoring System & Logging Databases")
    # TODO: add code to set up monitoring system and logging databases
