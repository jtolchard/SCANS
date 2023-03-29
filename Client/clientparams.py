# client parameter file for SCANS
# DEVELOPMENT VERSION
#
# This file defines which metrics are scraped every hour.
# File paths for standard Bruker MICS logs are provided, but any log file(s) can 
# be used# by revising the path, delim, and positional arguments. New metrics can
# be added by creating new dictionary blocks. For new metrics, 'dockerpath'
# should follow the format "/root/scans/logs/<metric.'name'>.log".
# Please consult the README for how to install and setup mics correctly.
#
# The default parameters are setup for standard MICS log files:
#'path': '/opt/Bruker/mics/logs/heliumlogcache.log',
#'path': '/opt/Bruker/mics/logs/rtshims.log',
#'path': '/opt/Bruker/mics/logs/field.log',
#'path': '/opt/Bruker/mics/logs/events.log', 
#'path': '/opt/Bruker/mics/logs/events.log', 

#Name to be associated with this machine
system_name = '600 MHz'

# Do not include white space in any item
helium_level = {
    'name': 'helium_level',                                                     # Name of the variable
    'use': True,                                                                # Should this variable be scraped / is it setup
    'path': '/Users/James/Code/NMR/SCANS/TestData/600MHz_heliumlogcache.log',   # Path pointing to live logs
    'dockerpath': '/root/scans/logs/helium_level.log',                          # DO NOT EDIT - mounted volume path used in container env
    'delim': ';',                                                               # The delimiter used by the file
    'datestamp_position': 0,                                                    # The position of the time/date data in the row (starts at zero!)
    'datavalue_position': 1,                                                    # The position of the data value in the row (starts at zero!) 
    'units': '%'                                                                # Desired unit of the output values
}

shim_temp = {
    'name': 'shim_temperature',
    'use': True,
    'path': '/Users/James/Code/NMR/SCANS/TestData/rtshims.log',
    'dockerpath': '/root/scans/logs/shim_temperature.log',
    'delim': ';',
    'datestamp_position': 0,
    'datavalue_position': 1,
    'units': 'C'
}

#YOU NEED TO LOOK INTO WHICH FIELD PARAM IS BEST TO CHECK
B0_field = {
    'name': 'B0_field',
    'use': True,
    'path': '/Users/James/Code/NMR/SCANS/TestData/field.log',
    'dockerpath': '/root/scans/logs/B0_field.log',
    'delim': ';',
    'datestamp_position': 0,
    'datavalue_position': 2,
    'units': ' MHz'
}

events = {
    'name': 'events',
    'use': True,
    'path': '/Users/James/Code/NMR/SCANS/TestData/events.log',
    'dockerpath': '/root/scans/logs/events.log',
    'delim': ';',
    'datestamp_position': 0,
    'datavalue_position': 2,
    'units': ''
}

emptyexample = {
    'name': 'emptyexample',
    'use': True,
    'path': '/Users/James/Code/NMR/SCANS/TestData/empty.log',
    'dockerpath': '/root/scans/logs/emptyexample.log',
    'delim': ';',
    'datestamp_position': 0,
    'datavalue_position': 2,
    'units': ''
}