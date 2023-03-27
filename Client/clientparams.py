# client parameter file for SCANS
#
# This file defines which metrics are scraped every hour. # The default parameters are setup for standard MICS log files, but any log file can be consulted by revising the path, delim, and positional arguments.
# If you do use MICS, set 'use_mics' to true, and the script will regularly check if the mics process is running.
# Please consult the README for how to install and setup mics correctly.

system_name = '600 MHz'

#Is the system using mics?
use_mics = True

helium = {
    'name': 'helium',                                   # Name of the variable
    'Use': True,                                        # Should this variable be scraped / is it setup
    'path': '/opt/Bruker/mics/logs/heliumlogcache.log', # The path to the relevat log file 
    'delim': ';',                                       # The delimiter used by the file
    'datestamp_position': '0',                          # The position of the time/date data in the row (starts at zero!)
    'datavalue_position': '1'                           # The position of the datav alue in the row (starts at zero!) 
}

shim_temp = {
    'name': 'shim temperature',                                   
    'Use': True,                                       
    'path': '/opt/Bruker/mics/logs/rtshims.log', 
    'delim': ';',                                       
    'datestamp_position': '0',                          
    'datavalue_position': '1'                           
}

#YOU NEED TO LOOK INTO WHICH FIELD PARAM IS BEST TO CHECK
B0_field = {
    'name': 'B0_field',                                   
    'Use': True,                                       
    'path': '/opt/Bruker/mics/logs/field.log', 
    'delim': ';',                                       
    'datestamp_position': '0',                          
    'datavalue_position': '3'                           
}

events = {
    'name': 'events',                                   
    'Use': True,                                       
    'path': '/opt/Bruker/mics/logs/events.log', 
    'delim': ';',                                       
    'datestamp_position': '0',                          
    'datavalue_position': '3'                           
}