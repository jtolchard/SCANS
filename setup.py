"""Setup script for SCANS NMR Monitoring
Installer does not take any arguments, should be run with: "python3 installer.py"
Only requirements are that docker and docker-compose are correctly installed (i.e.
their executables are available in your path. The paths and log files named in
this file should not be changed. 

## NOT SURE YET
The output of the installer will be a ./bin folder containing scripts
that are correctly configured to load and monitor the log files on your system.
"""

# Boilerplate
__author__ = "James Tolchard"
__license__ = "GPLV3"
__version__ = "0.5"
__maintainer__ = "James Tolchard"
__email__ = "james.tolchard@univ-lyon1.fr"
__status__ = "Development"

# Imports
import subprocess
import os
import socket

# Core variables
dependencies = ['docker','docker-compose']
bin_path = './bin/'

#Print ASCII header
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

# Check for necessary packages
def check_package(package_name):
    return subprocess.call(["command", "-v", package_name], stdout=subprocess.PIPE) == 0

# Obtain local IP addres
def localip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return(local_ip)




## RUN MAIN
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
#Print module selection
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
    count = 0
    while count != 1:
        spect_name = input("Choose a spectrometer name: ")
        chk = input(f"Set name to {spect_name}? (y/n): ")
        if chk == "y":
            count = 1

    # Updating grok
    grok_config_file = os.path.join("Client-spec", "configuration", "grok.yml")

    # Read current config file
    with open(grok_config_file, "r") as file:
        file_contents = file.read()
    
    updated_file_contents = file_contents.replace("$SPECT_NAME", spect_name)

    # Write new grok file
    with open(grok_config_file, "w") as file:
        file.write(updated_file_contents)
        print(f"grok config updated.\n")

    # Print out target line for user 
    ip_address = localip()
    print(f"Done.\nEnsure the docker-compose.yml file for you monitoring system(s) contains the new 'extra_hosts' line")
    print(f'- "{spect_name}:{ip_address}"')

# Setup for server logging container
elif menu_entry_index == 1:
    print("Setting up Server/RAID Logging module")
    # TODO: add code to set up server and RAID logging module

# Setup for monitoring container
elif menu_entry_index == 2:
    print("Setting up Monitoring System & Logging Databases")
    # TODO: add code to set up monitoring system and logging databases


