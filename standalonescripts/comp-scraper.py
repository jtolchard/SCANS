import argparse
from pymodbus.client import ModbusSerialClient
import csv
import time

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serialport', required=True, help='The path to the serial port device for the Modbus connection')
parser.add_argument('-f', '--filepath', help='Path to the log file')
parser.add_argument('-p', '--prettyoutput', action='store_true', help='Print pretty output to standard output')
parser.add_argument('-t', '--timing', action='store_true', help='Enable script timing')
args = parser.parse_args()

# Serial port
SERIAL_PORT = args.serialport

# CSV file path
csv_file_path = args.filepath

# Start the timer if timing is enabled
if args.timing:
    start_time = time.time()

# Modbus RTU connection parameters
BAUDRATE = 9600              # Serial port baud rate
PARITY = 'N'                 # Parity ('N': None, 'E': Even, 'O': Odd)
STOPBITS = 1                 # Number of stop bits
BYTESIZE = 8                 # Number of data bits
UNIT_ID = 1                  # Modbus unit ID

# A dictionary with register addresses and their properties (from BAUER documentation)
address_dict = {
    0: {'name': 'output pressure', 'scale': 10, 'result': None, 'unit': 'bar'},
    2: {'name': 'input pressure', 'scale': 100, 'result': None, 'unit': 'bar'},
    10: {'name': 'gas balloon %', 'scale': 10, 'result': None, 'unit': '%'},
    11: {'name': 'cooling air temp', 'scale': 10, 'result': None, 'unit': 'C'},
    12: {'name': 'last stage temp', 'scale': 10, 'result': None, 'unit': 'C'},
    13: {'name': '1st stage temp', 'scale': 10, 'result': None, 'unit': 'C'},
    14: {'name': '2nd stage temp', 'scale': 10, 'result': None, 'unit': 'C'},
    15: {'name': '3rd stage temp', 'scale': 10, 'result': None, 'unit': 'C'},
    16: {'name': '4th stage temp', 'scale': 10, 'result': None, 'unit': 'C'},
    35: {'name': 'operating hours', 'scale': 1, 'result': None, 'unit': 'hrs'},
    50: {'name': 'alarms & messages 1', 'scale': 1, 'result': None, 'unit': ''},
    51: {'name': 'alarms & messages 2', 'scale': 1, 'result': None, 'unit': ''},
    52: {'name': 'alarms & messages 3', 'scale': 1, 'result': None, 'unit': ''},
    53: {'name': 'alarms & messages 4', 'scale': 1, 'result': None, 'unit': ''},
    54: {'name': 'alarms & messages 5', 'scale': 1, 'result': None, 'unit': ''},
    55: {'name': 'alarms & messages 6', 'scale': 1, 'result': None, 'unit': ''},
     56: {'name': 'alarms & messages 7', 'scale': 1, 'result': None, 'unit': ''},
    57: {'name': 'alarms & messages 8', 'scale': 1, 'result': None, 'unit': ''}
}

def read_modbus_registers():
    try:
        client = ModbusSerialClient(method='rtu', port=SERIAL_PORT, baudrate=BAUDRATE, parity=PARITY,
                                    stopbits=STOPBITS, bytesize=BYTESIZE, timeout=1)
        if not client.connect():
            print('Connection failed!')
            return

        for address, properties in address_dict.items():
            result = client.read_holding_registers(address, count=1, unit=UNIT_ID)
            if result.isError():
                print(f'Error reading register {address}: {result}')
            else:
                value = result.registers[0]
                
                if properties['scale'] >1:
                    properties['result'] = value / properties['scale']
                else:
                    properties['result'] = value

        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

def write_to_stdout_pretty():
    print("Register values:")
    for address, properties in address_dict.items():
        print(f"Address: {address}, Name: {properties['name']}, Result: {properties['result']} {properties['unit']}")

def write_to_log_file():
    try:
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([properties['name'], properties['result'], properties['unit']])
    except Exception as e:
        print(f'Error writing to log file: {e}')

def csv_file_exists():
    try:
        with open(csv_file_path, 'r') as csvfile:
            return csvfile.read().strip() != ''
    except FileNotFoundError:
        return False
    
def write_header_to_csv():
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header_row = ['#' + item['name'] for item in address_dict.values()]
        writer.writerow(header_row)

def clear_data_lines_in_csv():
    with open(csv_file_path, 'r') as csvfile:
        lines = csvfile.readlines()
        if len(lines) >= 11:
            with open(csv_file_path, 'w', newline='') as csvfile:
                csvfile.write(lines[0])

def write_data_to_csv(data_row):
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_row)

def masterWriter():
     # Check if csv file exists or is empty
    if not csv_file_exists():
        # Write the header row to the CSV file
        write_header_to_csv()
    else:
        # Clear data lines in the csv file if it exists and is 10 lines or longer
        clear_data_lines_in_csv()

    # Create a data row and write to file
    csv_row = create_csv_row()
    write_data_to_csv(csv_row)

def create_csv_row():
    return [str(item['result']) for item in address_dict.values()]

#def create_csv_row():
#    csv_row = []
#    for item in address_dict.values():
#        result = str(item['result'])
#        name = item['name']
#        if 'alarms & messages' in name:
#            decimal_result = int(result)
#            binary_result = bin(decimal_result)[2:].zfill(16)
#            csv_row.append(binary_result)
#        else:
#            csv_row.append(result)
#    return csv_row

# Read Modbus registers
read_modbus_registers()

# Write output to STDOUT or log file based on the presence of filepath and prettyoutput flag
if args.filepath and args.prettyoutput:
    masterWriter()
    write_to_stdout_pretty()
elif args.prettyoutput:
    write_to_stdout_pretty()
else:
    csv_row = create_csv_row()
    print(csv_row)

# Calculate and print the script execution time if timing is enabled
if args.timing:
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'Script execution time: {execution_time} seconds')

