import paramiko
import argparse
import csv
import ast

# Example usage
hostname = "192.168.103.215"
username = "crmn"
private_key_path = "/app/private_key"
command = "/opt/local/bin/python3.9 /Users/crmn/CRMN_Monitoring/SCANS/standalonescripts/comp-scraper.py -s /dev/tty.usbserial-00004004"

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filepath', help='Path to the log file')
args = parser.parse_args()

# CSV file path
if args.filepath:
    csv_file_path = args.filepath
else:
    csv_file_path = "/app/logs/log.txt"

def run_ssh_command(hostname, username, private_key_path, command):
    # Create an SSH client
    client = paramiko.SSHClient()

    # Automatically add the host key
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

        # Connect to the SSH server using the private key
        client.connect(hostname=hostname, username=username, pkey=private_key)

        # Run the command
        stdin, stdout, stderr = client.exec_command(command)

        # Read the STDOUT
        stdout = stdout.read().decode()
        output_list = ast.literal_eval(stdout)
        output_string = ', '.join(output_list)

        # Print the output
        return output_string

    except paramiko.AuthenticationException:
        print("Authentication failed.")
    except paramiko.SSHException as e:
        print("SSH connection error:", str(e))
    finally:
        # Close the SSH connection
        client.close()

def write_to_log_file(output_string):
    try:
        with open(csv_file_path, 'a', newline='') as file:
            file.write(output_string + '\n')
    except Exception as e:
        print(f'Error writing to log file: {e}')

def clear_data_lines_in_csv():
    try:
        with open(csv_file_path, 'r') as csvfile:
            lines = csvfile.readlines()
            if len(lines) >= 10:
                with open(csv_file_path, 'w', newline='') as csvfile:
                    csvfile.truncate(0)
    except Exception as e:
        print(f'Error clearing data lines in CSV: {e}')

def csv_file_exists():
    try:
        with open(csv_file_path, 'r') as csvfile:
            return csvfile.read().strip() != ''
    except FileNotFoundError:
        return False


def master_writer():
    # Clear the data lines in the CSV file

    if csv_file_exists():
        clear_data_lines_in_csv()

    # Execute the SSH command
    output = run_ssh_command(hostname, username, private_key_path, command)

    # Write output to STDOUT
    print(output)

    # Write output to the log file if filepath provided
    if csv_file_path:
        write_to_log_file(output)

# Execute the script
if __name__ == '__main__':
    master_writer()