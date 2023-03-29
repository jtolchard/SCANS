# SCANS
Simple Containerised Analysis for NMR Systems

## Overview
SCANS provides a simple system to monitor logfiles. It is geared towards computers attached to NMR spectrometers, but any system can 
be monitored, for example those attached to gyrotrons or compressors, as long as the logfiles are clearly delimited and contain a date
and a datapoint per row as minimum.

SCANS works using a series of python scripts within containerized environments which allows SCANS to be cross-platform and easy to setup.
The Docker system is used for containerization; more information about Docker and containerization can be found [here](https://www.docker.com/resources/what-container/).  

There are two flavours of container used by SCANS.  

### The Client
The SCANS client is installed on each spectrometer ot system that requires logging.
Prior to installation, a parameter file needs to be setup with the system name and the definitions (names, paths, units, column positions, etc.,) for all the required metrics.  
Multiple metrics can be scraped from the same file, and custom metrics can be added.  
The client can either be manually started via a command line command, or configured to run at boot time (see Installation notes).  
When running, the client will reguarly check (default every 60 seconds) for updates to the noted log files.  


## Setting up mics on Bruker systems



## INSTALLATION





## NOTES:
- Do not edit/delete the files in the logging directory, as these are mount points for the SCANS scraper. If you do, you will need to stop and restart SCANS