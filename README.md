<img width="1834" alt="Make your README2" src="https://github.com/jtolchard/SCANS/assets/50239502/9192c740-109a-4b6d-b935-cd2844792e58">

# SCANS
SCANS brings together multiple open-source tools and custom Python scripts to provide basic dashboard monitoring, with easily customizable analysis and data visualisations. It was created with NMR laboratories in mind, however, data from any system can easily be incorporated. Provided examples include monitoring RAID-array capacity, API-retrieved data mining, Bruker-HLMU web-scraping, and monitoring of industrial hardware such as compressors (via serial-USB ModBus-RTU connection). 

_Disclaimer... for the moment, SCANS is simple in its analysis and compute requirements but less-so in its manual setup. I am working towards an automated setup tool._

## Overview





SCANS works using a series of python scripts within containerized environments which allows SCANS to be secure, cross-platform, and easy to setup.

The Docker system is used for containerization; more information about Docker and containerization can be found [here](https://www.docker.com/resources/what-container/).  

<ins>**SCANS employs two flavours of container:**</ins>

* <ins>**The Client**</ins>  
The SCANS client is installed on each spectrometer or system that requires logging.
Prior to installation, a parameter file should be setup with the system name and the definitions (names, paths, units, column positions, etc.,) for all the required metrics.
Multiple metrics can be scraped from the same file and custom metrics can also be added. After installation, the client can either be manually started via the command line or configured to run 
automatically at boot time (see Installation notes). When running, the client will reguarly check (by default every 60 seconds) for updates to the defined log files and create a aggregated 
singular log file, with each record stored as a python dictionary.

* <ins>**The Controller**</ins>  
The SCANS controller should be installed on a single computer, ideally one which is permanently online. It will gather metrics across all SCAN clients of a given network and provide a web interface for viewing the metric data.
Future implementations of SCANS will comprise elements of system monitoring and user administration.


## Setting up mics on Bruker systems

For Bruker systems, the Management Information Control System (MICS) provides a platform for the routine logging of spectrometer-related metrics.
On Bruker systems, SCANS will therefore predominatly refer to log files stored by MICS.
If your systems are not already running MICS, please consult the Official Installation Instructions, [for example here.]](http://mics.bruker.com/micsapp/docs/mics_manual.pdf)
This should result in a series of regulary updates logfiles, available at _/opt/Bruker/mics/logs._ Typical metrics include the daily helium level, shim currents, B0_field monitoring, and system events. Although uncommon, Nitrogen-level monitoring  will also be available on systems equipped with a nitrogen-level sensor. 

## INSTALLATION of SCANS

The main SCANS package can be downloaded with the following command:  
<ins>** WHEN REPO GOES PUBLIC **</ins>  
wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip

<ins>**For each client machine**</ins>  
Unpack the repository in a suitable location  and move to the Client directory:  
```
    wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip
    unzip main.zip
    mv main SCANS  
    cd SCANS/Client  
```  
  
Open clientparams.py with a text editor and revise the number and nature of any desired metrics. 
Each metric is stored as a Python dictionary (within curly braces), for example:  
```  
helium_level = {  
    'name': 'helium_level',                              # Name of the variable  
    'use': True,                                         # Should this variable be scraped?
    'path': '/opt/Bruker/mics/logs/heliumlogcache.log',  # Path pointing to live logs  
    'dockerpath': '/root/scans/logs/helium_level.log',   # DO NOT EDIT - mounted volume path used in container env  
    'delim': ';',                                        # The delimiter used by the logfile  
    'datestamp_position': 0,                             # The column position of the time/date data in the row (starts at zero!)  
    'datavalue_position': 1,                             # The column position of the data value in the row (starts at zero!)   
    'units': '%'                                         # Desired unit of the output values  
}  
```

You can add any additional metrics by creating new blocks.  
  
It is fine to reference any log files that are currently empty, however the inclusion of incorrect paths will halt the installer.
Configuration and installation should therefore be done after any logging software (i.e, MICS) has been setup.

<ins>Remember to set the system_name at the top of clientparams.py to distinguish your specific machine.</ins>

<ins>**Docker**</ins>  
You will also need to install Docker to manage the SCANS docker-containers. The easiest method is to run:

`sudo yum install docker` # if you are on a CentOS /rpm system  
or  
`sudo apt-install docker` # if you are on a Debian / deb system.

SCANS (client or controller) will run seemlessly [on MacOS (Intel and Apple Silicon)](https://docs.docker.com/desktop/install/mac-install/). 
Alternatively, you can also install docker via a package manager such as homebrew or ports.

SCANS has not currently been tested on Windows.
I don't see why SCANS wouldn't work well within Windows Subsystem for Linux  (WSL) - but this will require Windows 10 or greater.
I will investigate installation on older systems.  
  
Once Docker is installed, you simply have to run the installer with:  

```  
python3 installer.py --full  
```  
This will create a <ins>SCANS/Client/bin/</ins> directory with five scripts specific to your system:  
```  
scans_start       # Start the monitoring process.  
scans_build+start # Fully parse all available logs to date and start the monitoring process.  
scans_rebuild     # Fully parse all available logs and create aggregated log. Do not run monitoring process.  
scans_stop        # Stop monitoring.  
scans_status      # Read the log file that SCANS creates as it runs. Confirms scans is running and can be useful for troubleshooting.  
```  

For first-time installations, the `bin/scans_build+start` is recommended. 

This can be run manually from the command line, or run as a system process to start SCANS automatically upon boot.
This can be done by:  
```  
sudo cp service /etc/systemd/scans_client.service  
sudo systemctl  
sudo systemctl daemon-reload  
sudo systemctl start scans_client.service 
sudo systemctl status scans_client.service
sudo systemctl enable scans_client.service
```  

Should you wish to disable SCANS starting at boot time, you can use:  
`sudo systemctl disable scans_client.service`  
  
If you would like frequent command line access to SCANS, you can add the bin directory to your UNIX path ([online how-to](https://phoenixnap.com/kb/linux-add-to-path)).  


## NOTES:  
- Do not edit/delete the files in the logging directory, as these are mount points for the SCANS scraper. If you do, you will need to stop and restart SCANS  

## TO ADD:  
NEED TO LOOK INTO VERYFYING DOCKER DAEMON IS RUNNING BEFORE RUNTIME!
Create a check to see if SCANS is running as a system service?  
Information for HLMU units?  
Create a schematic for the readme showing the container and the Client:Controller system

## SOURCES:  
http://www2.chem.uic.edu/nmr/downloads/bruker/en-US/pdf/z31735.pdf
