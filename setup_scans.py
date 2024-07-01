"""
The main setup script for SCANS
The SCANS installer does not take any arguments and should be run as root (or sudo)
with: "sudo python3 setup.py"
"""

## Boilerplate
__author__ = "James Tolchard"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "James Tolchard"
__email__ = "james.tolchard@univ-lyon1.fr"
__status__ = "Production"

import os
import sys
import shutil
import socket
import re
import glob
import subprocess
import yaml

# List of required program dependencies
core_dependencies = ['docker', 'docker-compose']

# Define useful paths
container_blocks = './Modules/Client-spec/setup/blocks.yml'
default_diskless_logs = '/usr/diskless/prog/logfiles'
default_mics_logs = '/opt/Bruker/mics/logs'

def check_core_dependencies(dependencies):
    """
    Check if required dependencies are available.
    
    Args:
        dependencies (list): List of required dependencies.
    
    Returns:
        list: List of missing dependencies.
    """
    missing_dependencies = [prog for prog in dependencies if shutil.which(prog) is None]
    return missing_dependencies

def get_local_ip():
    """
    Obtain the local IP address.
    
    Returns:
        str: Local IP address or None if an error occurs.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error:
        return None

def get_user_input(prompt):
    """
    Read and double-check user input for a custom question, ensuring no whitespace or blanks.
    
    Args:
        prompt (str): The prompt text to display to the user.
    
    Returns:
        str: Validated user input.
    """
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Input cannot be empty. Please try again.")
        elif any(char.isspace() for char in user_input):
            print("Input contains whitespace. Please try again.")
        else:
            confirm = input(f"Use {user_input}? (y/n): ").strip().lower()
            if confirm == 'y':
                return user_input

def ask_multiple_choice(question, choices):
    """
    Ask the user a multiple choice question.
    
    Args:
        question (str): The question text.
        choices (list): List of choices.
    
    Returns:
        int: The user's choice index.
    """
    while True:
        print(question)
        for i, choice in enumerate(choices, 1):
            print(f"\t{i}: {choice}")
        response = input("\nChoice: ").strip()
        
        if response.isdigit() and 1 <= int(response) <= len(choices):
            return int(response)
        else:
            print("Invalid input. Please enter the number corresponding to your choice.")

def check_path(module):
    """
    Check for the existence of a relative directory.
    
    Args:
        module (str): The module name.
    
    Exits:
        If the directory does not exist.
    """
    relative_path = os.path.join('Modules', module)
    if not os.path.isdir(relative_path):
        print(f"\nThe {module} module could not be found. Please invoke the script from the top SCANS directory.\n")
        sys.exit(1)

def check_log_file(path, log_files):
    """
    Check whether any log file from a list exists at a certain location.
    
    Args:
        path (str): The directory path.
        log_files (list): A list of log file names.
    
    Returns:
        tuple: Validated path to the log file and the log file name.
    """
    for log_file in log_files:

        full_path = os.path.join(path, log_file) 

        if os.path.isfile(full_path):
            return path, log_file
    
    print(f"Log files were not found in their directory ({path})")
    path = input("Please enter the absolute path of the folder which contains the spectrometer log files: ").strip()
    return check_log_file(path, log_files)

def check_existing_config(path, items):
    """
    Check for existing configuration files or directories and prompt for removal.
    
    Args:
        path (str): The base path.
        items (list): List of configuration items.
    
    Exits:
        If the user chooses not to remove existing configuration.
    """
    found_items = [os.path.join(path, item) for item in items if os.path.exists(os.path.join(path, item))]
    if found_items:
        response = input("Configuration files or directories already exist. "
                         "Do you want to remove them and start a fresh installation? "
                         "This cannot be undone. (y/n): ").strip().lower()
        if response == 'y':
            for item_path in found_items:
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    print(f"An error occurred while removing {item_path}: {e}")
            print("The previous configuration files were removed.")
        else:
            print("Setup cancelled.")
            sys.exit(0)

def extract_labels(file_path):
    # Read the last line of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        last_line = lines[-1].strip()
    
    # Find the position of the last colon
    last_colon_pos = last_line.rfind(':')
    
    # Extract the part of the line after the last colon
    data_part = last_line[last_colon_pos + 1:].strip()
    
    # Define a regular expression pattern to match the labels and their values
    pattern = re.compile(r'([^,=]+?)\s*=\s*[^,]+')
    
    # Find all matches in the data part
    matches = pattern.findall(data_part)
    
    # Strip any leading/trailing whitespace from labels
    labels = [match.strip() for match in matches]
    
    return labels

def load_configurations(yaml_file):
    """
    Load configurations from a YAML file.

    Args:
        yaml_file (str): Path to the YAML file containing configuration mappings.

    Returns:
        dict: Dictionary containing the configuration mappings.
    """
    with open(yaml_file, 'r') as file:
        configurations = yaml.safe_load(file)
    return configurations

def build_container_file(metrics, path):
    """
    Build Docker Compose configuration file based on provided metrics and path.

    Args:
        metrics (list): List of metrics to determine which Docker containers to include.
        path (str): Path to the directory containing log files.

    This function reads a template Docker Compose file, appends necessary blocks based on provided metrics,
    and inserts the log path into the Docker Compose configuration.

    Raises:
        FileNotFoundError: If the template Docker Compose file is not found.

    Notes:
        The function assumes the existence of specific YAML block formats in the template file.
    """
    # Load container configurations
    containers = load_configurations(container_blocks)
    
    # Initialize an empty list to store non-empty blocks
    non_empty_blocks = []
    
    # Evaluate conditions and collect non-empty blocks
    if any(item in metrics for item in ['helium.log', 'heliumlogcache.log','helium level']) and 'helium' in containers:
        helium_block = containers['helium']
        non_empty_blocks.append(format_container_block(helium_block))
    
    if any(item in metrics for item in ['nitrogen.log', 'nitrogenlogcache.log','nitrogen level']) and 'nitrogen' in containers:
        nitrogen_block = containers['nitrogen']
        non_empty_blocks.append(format_container_block(nitrogen_block))
    
    if any(item in metrics for item in ['field.log','field']) and 'field' in containers:
        field_block = containers['field']
        non_empty_blocks.append(format_container_block(field_block))

    if any(item in metrics for item in ['rtshims.log']) and 'shims' in containers:
        shims_block = containers['shims']
        non_empty_blocks.append(format_container_block(shims_block))

    if any(item in metrics for item in ['events.log']) and 'events' in containers:
        events_block = containers['events']
        non_empty_blocks.append(format_container_block(events_block))
    
    blank_dkr_cmp = './Modules/Client-spec/setup/scripts/docker-compose/blank_docker-compose.yml'
    destination = './Modules/Client-spec/docker-compose.yml'
    
    try:
        shutil.copy2(blank_dkr_cmp, destination)

        # Append non-empty blocks to the output file
        with open(destination, 'a') as output:
            for block in non_empty_blocks:
                output.write(block + "\n\n")

        # Add new log path to docker-compose file
        with open(destination, 'r') as file:
            file_contents = file.read()
        file_contents = file_contents.replace('{$log_path}', path)
        with open(destination, 'w') as file:
            file.write(file_contents)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")

def format_container_block(block):
    """
    Format a YAML block with specific indentation rules.

    Args:
        block (dict): Dictionary representing a YAML block.

    Returns:
        str: Formatted YAML block as a string.
    """
    yaml_lines = yaml.dump(block, default_flow_style=False).splitlines()
    formatted_lines = []
    for i, line in enumerate(yaml_lines):
        if i == 0:
            formatted_lines.append(f"  {line}")  # Indent first line by 2 spaces
        else:
            formatted_lines.append(f"  {line}")  # Indent subsequent lines by a further 2 spaces
    return "\n".join(formatted_lines)

def build_grok_config(method):
    """
    Copy the correcy Grok configuration files for specified method and path.

    Args:
        method (str): The method for configuring Grok ('mics', 'separate', or 'combined').
        path (str): Base path for configuring Grok.

    This function copies necessary Grok YAML files based on the specified method into the
    appropriate directory for configuration.

    Raises:
        OSError: If an error occurs during file operations (e.g., copying files).

    Notes:
        This function assumes specific directory structures for different Grok configurations.
    """
    if method == 'mics':
        config = './Modules/Client-spec/setup/scripts/grok/mics'
    elif method == 'separate':
        config = './Modules/Client-spec/setup/scripts/grok/diskless_multi'
    elif method == 'combined':
        config = './Modules/Client-spec/setup/scripts/grok/diskless_single'
    else:
        print("Error in setup code.")
        sys.exit(1)

    try:

        # Copy specific grok yml files
        os.makedirs('./Modules/Client-spec/configuration', exist_ok=True)
        for item in os.listdir(config):
            src_item = os.path.join(config, item)
            dst_item = os.path.join('./Modules/Client-spec/configuration', item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)
        print("\nConfiguration files copied\n")
    
    except Exception as e:
        print(f"An error occurred while configuring: {e}")
        sys.exit(1)

def get_machines():
    ip_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$')
    print("\nYou must provide the network information for all of your clients.\n")
    entries = []
    first_entry = True  # Flag to check if it's the first entry attempt

    while True:
        while True:
            name = input("Please enter a machine name (or type 'done' to finish): ").strip()
            if name.lower() == 'done' and first_entry:
                print("You must enter at least one machine name and IP address before finishing.")
                continue
            if name.lower() == 'done':
                return entries
            if name == '':
                print("Names cannot be blank. Please try again.")
                continue
            if re.search(r'\s', name):
                print("Names cannot contain white spaces. Please try again.")
                continue
            break

        while True:
            ip_address = input(f"Enter the IP address for {name}: ").strip()
            if ip_address == '':
                print("IP addresses cannot be blank. Please try again.")
                continue
            if re.search(r'\s', ip_address):
                print("IP addresses cannot contain white spaces. Please try again.")
                continue
            if not ip_pattern.match(ip_address):
                print("Invalid IP address format. Please enter a valid IP address (XXX.XXX.XXX.XXX).")
                continue
            break

        # Confirm entry
        print(f"Name: {name}, IP Address: {ip_address}")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        if confirm == 'y':
            entries.append(f'"{name}:{ip_address}"')
            first_entry = False  # Set the flag to False after the first valid entry
        else:
            print("Entry discarded. Please re-enter the details.")

def is_port_open(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Set timeout to 1 second
        sock.connect((ip, int(port)))
        sock.close()
        return True
    except socket.error:
        return False
    
def main():
    """
    Main function to run the setup script.
    """
    # Print ASCII header
    print('''
    ___________________________________
      ____   ____    _    _   _ ____  
     / ___| / ___|  / \  | \ | / ___| 
     \___ \| |     / _ \ |  \| \___ \ 
      ___) | |___ / ___ \| |\  |___) |
     |____/ \____/_/   \_\_| \_|____/ 
     __________________________________
    ''')

    # Check for required system programs
    missing_dependencies = check_core_dependencies(core_dependencies)
    if not missing_dependencies:
        print(f"Dependencies satisfied: {', '.join(core_dependencies)}\n")
    else:
        print(f"The necessary programs ({', '.join(missing_dependencies)}) were not found in your path.")
        print("Please check your path or consult the INSTALL.md file for more information.\n")
        sys.exit(1)

    # Get IP local address
    ip_address = get_local_ip()
    if ip_address:
        print("LAN connection detected\n")
    else:
        print("Local IP address not found.\nSCANS is reliant on local network connectivity, so please check your network connection and repeat setup.")
        print("Exiting the script.")
        sys.exit(0)

    module_choices = ["Spectrometer logging", "Monitoring module"]
    module_answer = ask_multiple_choice("Which module do you want to setup?", module_choices)
    
    module_path = 'Client-spec' if module_answer == 1 else 'Monitor'
    check_existing_config(f'./Modules/{module_path}', ['configuration', 'docker-compose.yml'])
    

    if module_path == 'Monitor':
        print(f"\n{module_path} setup\n")
        setup_monitor(ip_address)
    elif module_path == 'Client-spec':
        print(f"\n{module_path} setup\n")
        setup_spectrometer(ip_address)

def setup_spectrometer(ip_address):
    """
    Setup function to initialize the chosen module.
    
    Args:
        ip_address (str): Local IP address.
        module (str): The module to setup.
    """
      
    log_choices = ["Diskless", "MICS"]
    log_answer = ask_multiple_choice("\nHow are your spectrometer logs currently created?", log_choices)
    log_type = 'diskless' if log_answer == 1 else 'mics'
    log_file = ['heliumlog','helium.log'] if log_type == 'diskless' else ['heliumlogcache.log']
        
    if log_answer == 1:
        path, log_file = check_log_file(default_diskless_logs, log_file)
    else:
        path, log_file = check_log_file(default_mics_logs, log_file)

    # Identify what logs and metrics you have
    # Cater for new diskless style logs
    if log_answer == 1 and log_file == 'heliumlog':
        metrics = extract_labels(os.path.join(path,log_file))
        #print(f'Found metrics: '+', '.join(metrics))
        method = 'combined'
        
    # Cater for old diskless style logs
    elif log_answer == 1 and log_file == 'helium.log':
        metrics = [os.path.basename(f) for f in glob.glob(os.path.join(path,'*.log')) if os.path.getsize(f) > 0]
        #print(f'Found logs: '+', '.join(metrics))
        method = 'separate'
        
    # Cater for MICS logs
    elif log_answer == 2:
        metrics = [os.path.basename(f) for f in glob.glob(os.path.join(path,'*.log')) if os.path.getsize(f) > 0]
        #print(f'Found logs: '+', '.join(metrics))
        method = 'mics'

    # Else, something is wrong..
    else:
        print("The log file configuration doesn't match with known format. Please contact the developer for assistance.")
        sys.exit(1)
       
    # Create the appropriate containers
    build_container_file(metrics,path)
    # Create the grok configuration files
    build_grok_config(method)
    # Print user message
    print(f'\nBuilt containers for: '+', '.join(metrics)+" metrics.")
    print(f'Setup complete.')
    print(f'\nLocal IP = {ip_address}\nPlease note this information for configuration of your monitoring module.\n')
    print('\nTo run your containers, please run the following:')
    print('cd ./Modules/Client-spec/')
    #print('sudo docker-compose build') #Required for custom images!
    print('sudo docker-compose up &\n')

def setup_monitor(ip_address):
    # Prepare base docker compose file
    blank_dkr_cmp = './Modules/Monitor/setup/scripts/docker-compose/blank_docker-compose.yml'
    destination = './Modules/Monitor/docker-compose.yml'
    
    server_alias = get_user_input("Choose a unique alias for this machine (e.g., LabServer): ")
    grafana_password = get_user_input("\nChoose an admin password for grafana's web interface\nN.B - this will be stored as free text in the config!: ")

    # Prep extra hosts aliases
    machines = get_machines()
    formatted_entries = "\n      - ".join(machines)

    try:
        #Create blank docker-compose file
        shutil.copy2(blank_dkr_cmp, destination)

        # Open new docker-compose file
        with open(destination, 'r') as file:
            file_contents = file.read()

        # Update place-holders in new docker-compose file
        file_contents = file_contents.replace('{$server_name}', server_alias)
        file_contents = file_contents.replace('{$server_ip}', ip_address)
        file_contents = file_contents.replace('{$grafana_password}', grafana_password)
        file_contents = file_contents.replace('{$extra_hosts}', f"      - {formatted_entries}")

        with open(destination, 'w') as file:
            file.write(file_contents)

    except FileNotFoundError as e:
        print(f"Error creating docker-compose file: {e}")

    try:
        # Copy blank config files
        config_dir = './Modules/Monitor/setup/configuration'
        destination = './Modules/Monitor/configuration'
        shutil.copytree(config_dir, destination, dirs_exist_ok=True)

        prom_short_yml = './Modules/Monitor/configuration/prom-short.yml'
        prom_long_yml = './Modules/Monitor/configuration/prom-long.yml'
        all_clients = [re.sub(r':[^"]+', ':9100"', item) for item in machines]
        all_clients = ', '.join(all_clients)

        # Deal with prom short file
        with open(prom_short_yml, 'r') as file:
            file_contents = file.read()

        # Update place-holders in new docker-compose file
        file_contents = file_contents.replace('{$server_name}', server_alias)
        file_contents = file_contents.replace('{$all_clients}', all_clients)

        with open(prom_short_yml, 'w') as file:
            file.write(file_contents)

         # Deal with prom long file
        print("\nSetup will now scan for active containers on these machines.")
        print("If any containers are not up and running, they will be missed, but can be added at a later date.")
        input("Press enter when ready!")

        services_ports = {"helium": "9144", "nitrogen": "9145", "field": "9146", "shim": "9147", "events": "9148"}
        # Initialize lists for each service
        helium_list = []
        nitrogen_list = []
        field_list = []
        shim_list = []
        events_list = []

        # Initialize dictionary to store services found for each machine name  (purely aesthetic!)
        machine_services = {}

         # Process each machine IP
        for machine_ip in machines:
            # Extract machine name and IP address
            parts = machine_ip.strip('"').split(':')
            machine_name = parts[0]
            ip_address = parts[1]

            # Initialize list to store services found for current machine
            if machine_name not in machine_services:
                machine_services[machine_name] = []

            # Check each service port for activity
            for service, port in services_ports.items():
                if ',' in port:
                    port_list = port.split(',')
                    for p in port_list:
                        if is_port_open(ip_address, p):
                            machine_services[machine_name].append(service)
                            if service == "helium":
                                helium_list.append(f'"{machine_name}:{p}"')
                            elif service == "nitrogen":
                                nitrogen_list.append(f'"{machine_name}:{p}"')
                            elif service == "field":
                                field_list.append(f'"{machine_name}:{p}"')
                            elif service == "shim":
                                shim_list.append(f'"{machine_name}:{p}"')
                            elif service == "events":
                                events_list.append(f'"{machine_name}:{p}"')
                else:
                    if is_port_open(ip_address, port):
                        machine_services[machine_name].append(service)
                        if service == "helium":
                            helium_list.append(f'"{machine_name}:{port}"')
                        elif service == "nitrogen":
                            nitrogen_list.append(f'"{machine_name}:{port}"')
                        elif service == "field":
                            field_list.append(f'"{machine_name}:{port}"')
                        elif service == "shim":
                            shim_list.append(f'"{machine_name}:{port}"')
                        elif service == "events":
                            events_list.append(f'"{machine_name}:{port}"')

        helium_list = ', '.join(helium_list)
        nitrogen_list = ', '.join(nitrogen_list)
        field_list = ', '.join(field_list)
        shim_list = ', '.join(shim_list)
        events_list = ', '.join(events_list)

        # Deal with prom long file
        with open(prom_long_yml, 'r') as file:
            file_contents = file.read()

        # Update place-holders in new docker-compose file
        file_contents = file_contents.replace('{$server_name}', server_alias)
        file_contents = file_contents.replace('{$server_ip}', ip_address)
        file_contents = file_contents.replace('{$helium_clients}', helium_list)
        file_contents = file_contents.replace('{$nitrogen_clients}', nitrogen_list)
        file_contents = file_contents.replace('{$field_clients}', field_list)
        file_contents = file_contents.replace('{$shim_clients}', shim_list)
        file_contents = file_contents.replace('{$events_clients}', events_list)

        with open(prom_long_yml, 'w') as file:
            file.write(file_contents)

        # PRINT SUMMARY
        print("\nService summary:")
        for machine_name, services_found in machine_services.items():
            services_list = ', '.join(set(services_found))  # Use set to remove duplicates
            print(f"{machine_name}: {services_list}")

    except FileNotFoundError as e:
        print(f"Error creating configuration files: {e}")

    print(f'\nSetup complete.')
    print('\nTo run your containers, please run the following:')
    print('cd ./Modules/Monitor/')
    #print('sudo docker-compose build') #Required for custom images!
    print('sudo docker-compose up &')
    print(f'\nYou will then be able to access your grafana instance at http://{ip_address}:3000')

if __name__ == "__main__":
    if os.geteuid() == 0:
        main()
    else:
        print("\nPlease run setup with elevated privileges (sudo/root)\n")
        sys.exit(1)
