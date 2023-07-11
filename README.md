<img width="1834" alt="banner" src="https://github.com/jtolchard/SCANS/assets/50239502/45bbe5c9-82d0-41dd-93d6-5766a50159d7">

# SCANS
SCANS brings together multiple open-source tools and custom Python scripts to provide basic dashboard monitoring, with easily customizable analysis, data visualisations, and alert management. It was created with NMR laboratories in mind, however, data from any system can be incorporated or be the sole focus. Provided examples include monitoring of auto-generated NMR Spectrometer logs (Bruker/MICS), RAID-array capacity, API-retrieved data mining, non-API web-scraping (Bruker-HLMU), and monitoring of industrial hardware such as compressors (via ModBus-RTU). 

<ins>_Disclaimer: for the moment, SCANS is simple in its analysis and compute requirements but less so in its manual setup. You don't need to be skilled in programming - but knowledge of regex and proficiency with UNIX systems are recommended. I aim to create an automated setup tool in the future._</ins>

## Overview
SCANS is built on top of various containerised services. These allow SCANS to be lightweight, modular, and generally cross-platform. The _Docker_ system is used for containerization; more information about Docker and containerization can be found [here](https://www.docker.com/resources/what-container/). 

### Containerisation
Containers are analogous to virtual machines. They are virtualised computing environments which can be configured with their own mounted drives, network interfaces, and runnable code. What initially defines a container is a container _image_. Images can be retrieved from public or private repositories, or built on an individual basis. Either way, an image is a static definition of a container _proper_. One container image can be used to spawn multiple containers of the same type and multiple containers of multiple types can be run at any one time on a _real_ computer _(but yes, container-inception [is a thing!](https://www.docker.com/resources/what-container/](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/) ))_. In the case of SCANS, containers are all run on real-world bare-metal machines, but containers are more commonly run from cloud platforms like AWS. Importantly, containers fundamentally share a host system's operating system kernel and so have strong performance, resource efficiency, and fast startup time compared to even the smallest Virtal Machine OS.

However, Virtual machines and Containers are principally different in their computational scope.

-   Virtual machines are typically associated with running a virtual instance of a whole, functioning operating system. For example, you might have explored installing a Linux OS like Ubuntu with a tool such as VirtualBox to test some software that only runs on Linux.
  
-   Virtual machines are now quite straightforward, but in many cases, are extreme overkill. You might have only wanted to test a small software package or a script and therefore didn't need any bloatware, browser, file explorer, word processor, or maybe even a GUI - and yet with the complete virtual machine, you would have downloaded, installed, and probably consuming your resources. Containers seek to address this problem.

- The ethos behind containerisation is that a container should do a singular, discrete task and only contain the code for the obligatory dependencies. They do not necessarily have to be small or computationally lightweight, but by structuring them this way, with discrete tasks broken down into separate, distinct containers - you provide the best opportunity to create lightweight, portable, and easy-to deploy-services.


## SCANS Containers and overall organisation

### Currentlu used container images

- <ins>**Grafana** ([image](https://hub.docker.com/r/grafana/grafana), [project](https://grafana.com/))</ins>  
  Grafana is a multi-platform open source analytics and interactive visualization web application. It provides charts, graphs, and alert management.   
- <ins>**Prometheus** ([image](https://hub.docker.com/r/prom/prometheus), [project](https://prometheus.io/))</ins>  
  Prometheus is a free software application used for event monitoring and alerting. It records metrics in a time series database built using an HTTP pull model, with flexible queries and real-time alerting.
- <ins>**grok_exporter** ([image](https://hub.docker.com/r/dalongrong/grok-exporter), [project](https://github.com/fstab/grok_exporter))</ins>  
  A community module to export Prometheus metrics from arbitrary unstructured log data using regex-like patterns.  
- <ins>**node_exporter** ([image](https://hub.docker.com/r/prom/node-exporter), [project](https://github.com/prometheus/node_exporter))</ins>
  A community module that exports predefined Prometheus metrics based upon typical linux-system log files and commands.  
- <ins>**dellhw_exporter** ([image](https://hub.docker.com/r/galexrt/dellhw_exporter), [project](https://github.com/galexrt/dellhw_exporter))</ins>
  A community module that exports predefined Prometheus metrics for Dell Hardware components using Dell OMSA. 
- <ins>**python** ([image](https://hub.docker.com/_/python), [project](https://www.python.org/))</ins>
  Various configurable images supporting different versions and builds of python, and its dependencies. SCANS uses python 3.7 and 3.9 depending on the module. 
  
### Alerts




SCANS works using a series of python scripts within containerized environments which allows SCANS to be secure, cross-platform, and easy to setup.



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
