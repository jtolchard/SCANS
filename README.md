# SCANS
Simple Containerised Analysis for NMR Systems

## Overview
SCANS provides a simple system to monitor logfiles. It is geared towards computers attached to NMR spectrometers, but any system can 
be monitored, for example those attached to gyrotrons or compressors, as long as the logfiles are clearly delimited and contain a date
and a datapoint per row (as minimum). 

SCANS works using a series of python scripts within containerized environments which allows SCANS to be secure, cross-platform, and easy to setup.
The Docker system is used for containerization; more information about Docker and containerization can be found [here](https://www.docker.com/resources/what-container/).  

<ins>**SCANS employs two flavours of container:**</ins>

### <ins>The Client</ins>
The SCANS client is installed on each spectrometer or system that requires logging.  
  
Prior to installation, a parameter file should be setup with the system name and the definitions (names, paths, units, column positions, etc.,) for all the required metrics.
Multiple metrics can be scraped from the same file and custom metrics can also be added. After installation, the client can either be manually started via the command line or configured to run 
automatically at boot time (see Installation notes). When running, the client will reguarly check (by default every 60 seconds) for updates to the defined log files and create a aggregated 
singular log file, with each record stored as a python dictionary.

### <ins>The Controller</ins>
The SCANS controller should be installed on a single computer. It will gather metrics across all SCAN clients on a given network and provide a web interface for viewing the metric data.  
  
Future implementations of SCANS will comprise elements of system monitoring and user administration.


## Setting up mics on Bruker systems

For Bruker systems, the Management Information Control System (MICS) provides a platform for the routine logging of spectrometer-related metrics.
On Bruker systems, SCANS will therefore predominatly refer to log files stored by MICS.
If your systems are not already running MICS, please consult the Official Installation Instructions, [for example here.]](http://mics.bruker.com/micsapp/docs/mics_manual.pdf)
This should result in a series of regulary updates logfiles, available at _/opt/Bruker/mics/logs._ Typical metrics include the daily helium level, shim currents, B0_field monitoring, and system events. Although uncommon, Nitrogen-level monitoring  will also be available on systems equipped with a nitrogen-level sensor. 

## INSTALLATION of SCANS





## NOTES:
- Do not edit/delete the files in the logging directory, as these are mount points for the SCANS scraper. If you do, you will need to stop and restart SCANS