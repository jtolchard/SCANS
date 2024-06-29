<img width="1834" alt="banner" src="https://github.com/jtolchard/SCANS/assets/50239502/45bbe5c9-82d0-41dd-93d6-5766a50159d7">

# SCANS
SCANS brings together multiple open-source tools and custom Python scripts to provide basic dashboard monitoring, with easily customizable analysis, data visualisations, and alert management. It was created with NMR laboratories in mind, however, data from any system can be incorporated or be the sole focus. Provided examples include monitoring of auto-generated NMR Spectrometer logs (Bruker/MICS), Dell Server RAID-array capacity, API-retrieved data mining, non-API web-scraping (Bruker-HLMU, Socomec-UPS), and monitoring of industrial hardware such as compressors (via ModBus-RTU). 

<ins>_Disclaimer: for the moment, SCANS is simple in its analysis and compute requirements but less so in its manual setup. You don't need to be skilled in programming - but knowledge of regex and proficiency with UNIX systems are recommended.The creation of an automated setup tool is in progress._</ins>

## Overview
SCANS is built on top of various containerised services. These allow SCANS to be lightweight, modular, and generally cross-platform. The _Docker_ system is used for containerization; more information about Docker can be found [here](https://www.docker.com/resources/what-container/). 

### Containerisation
Containers are analogous to virtual machines. They are virtualised computing environments which can be configured with their own mounted drives, network interfaces, and runnable code. What initially defines a container is a container _image_. Images can be retrieved from public or private repositories, or built on an individual basis. Either way, an image is a static definition of a container _proper_. One container image can be used to spawn multiple containers of the same type and multiple containers of multiple types can be run at any one time on singular computer hardware. In the case of SCANS, containers are run on standard x86 Linux workstations, but containers are more commonly run from bare-metal or cloud platforms like AWS. Importantly, containers fundamentally share a host system's operating system kernel and so have strong performance, resource efficiency, and fast startup time compared to even the smallest Virtual Machine OS.

However, Virtual machines and Containers are principally different in their computational scope.

-   Virtual machines are typically associated with running a virtual instance of a whole, functioning operating system. For example, you might have explored installing a Linux OS like Ubuntu with a tool such as VirtualBox to test some software that only runs on Linux.
  
-   Virtual machines are now quite straightforward to work with, but in many cases, are extreme overkill. You might only wanted to test a small software package or a script and therefore don't need most of the features like a browser, file explorer, office packages, or maybe even a GUI. And yet with a complete virtual machine, you will download and install all of these elements, and probably have them consuming your resources. Containers seek to address this problem.

- The ethos behind containerisation is that a container should do a singular, distinct task and only contain the code for the obligatory dependencies. They do not necessarily have to be small or computationally lightweight but, by structuring them this way, with discrete tasks broken down into separate containers - you provide the best opportunity to create lightweight, portable, and easy-to-deploy services.


## SCANS Containers and overall organisation

### SCANS currently uses the following publicly available container images:

- <ins>**Grafana** ([image](https://hub.docker.com/r/grafana/grafana), [project](https://grafana.com/))</ins>  
  Grafana is a multi-platform open-source analytics and interactive visualization web application. It provides charts, graphs, and alert management.   
- <ins>**Prometheus** ([image](https://hub.docker.com/r/prom/prometheus), [project](https://prometheus.io/))</ins>  
  Prometheus is a free software application used for event monitoring and alerting. It records metrics in a time series database built using an HTTP pull model, with flexible queries and real-time alerting.
- <ins>**Blackbox_exporter** [image](https://hub.docker.com/r/prom/blackbox-exporter/), [project](https://github.com/prometheus/blackbox_exporter)</ins>
Blackbox exporter allows probing of remote endpoints over HTTP, HTTPS, DNS, TCP, ICMP and gRPC
- <ins>**grok_exporter** ([image](https://hub.docker.com/r/dalongrong/grok-exporter), [project](https://github.com/fstab/grok_exporter))</ins>  
  A community module that exports Prometheus metrics from arbitrary unstructured log data using regex-like patterns.  
- <ins>**node_exporter** ([image](https://hub.docker.com/r/prom/node-exporter), [project](https://github.com/prometheus/node_exporter))</ins>  
  A community module that exports predefined Prometheus metrics based upon typical Linux-system log files and commands.  
- <ins>**dellhw_exporter** ([image](https://hub.docker.com/r/galexrt/dellhw_exporter), [project](https://github.com/galexrt/dellhw_exporter))</ins>  
  A community module that exports predefined Prometheus metrics for Dell Hardware components using Dell OMSA. 
- <ins>**Python** ([image](https://hub.docker.com/_/python), [project](https://www.python.org/))</ins>  
  Various configurable images that support the different versions and builds of Python, and its dependencies. SCANS uses Python 3.7 and 3.9 depending on the module. 

### Ports
Each SCANS docker module is assigned a unique network port for communication. These ports can be fully isolated in the docker network sandbox, or be exposed and mapped to ports of the local interface of the host machine. The specific ports used by a module are defined in the related docker-compose file and are reflected in the relevant Prometheus database .yml configuration file. They are fully customizable but by default, these are:  
  
- 9090: Prometheus short-retention time database  
- 9091: Prometheus long-retention time database  
- 9100: Node exporter (computer metrics)  
- 9115: Blackbox exporter (custom network response times)  
- 9137: Dell Hardware metrics (RAID, etc.,)  
- 9144: helium level scraping (MICS, HMLU logs, or topspin logs)  
- 9145: nitrogen level scraping (MICS, HMLU logs, or topspin logs)  
- 9146: field metrics (MICS or topspin logs)  
- 9147: shim metrics (MICS or topspin logs)  
- 9148: event metrics (MICS or topspin logs)  
- 9149: Air Liquide Webscraped N2 tank metrics  
- 9150: Air Liquide Webscraped SPI N2 metrics  
- 9151: Compressor metrics (Bauer ModBus - Helium recycling)  
- 9152: Gyrotron logs (Helium HMLU logs)  
- 9153: Gyrotron logs (Nitrogen HMLU logs)
- 9154: UPS status scraping
- 9155: Custom Arduino Lab Sensor (temp/pressure/humidity

### Organisation  

SCANS is built upon a network of containerized environments and custom Python scripts. These modules were designed with security in mind and are 'read-only' with respect to your primary data. 

<ins>**SCANS has two general types of module:**</ins>

* <ins>**Client modules**</ins>  
Client moduless are installed on each system (e.g., spectrometer workstation) that requires logging. Clients can also be installed on behalf of a monitored system, e.g., a client can be set up on one machine and remotely scrape metrics from the machine or service of interest that can't speak for itself (i.e., a remote API or sensor). 
Before installation, a parameter file should be set up with the system name, the definitions (names, paths, units, column positions, etc.,) for all the required metrics and the paths of the log files to be scraped. Multiple metrics can be scraped from the same file. After installation, the client can either be manually started via the command line or configured to run automatically at boot time. When running, the client will regularly check for updates to the defined log files, which will then, in turn, trigger the refresh of a locally accessible web page that shows the results and conforms to the Prometheus text-based exposition format.

* <ins>**The Controller module**</ins>  
The SCANS controller should be installed on a single computer, ideally one which is permanently online. A controller should run at least one Prometheus, which will gather metrics across all SCAN clients on a given network. Prometheus also provides its own web interface for viewing the metric data.

The installation and setup of SCANS is described in the [INSTALL.md](https://github.com/jtolchard/SCANS/blob/main/INSTALL.md) file


## Acknowledgments
Many Thanks to [Nathan Rougier](https://scholar.google.com/citations?user=1PvYOwkAAAAJ&hl=en&oi=ao) for his 3D printed models and renders!
Icons for Grafana alerts were adapted from those at https://thenounproject.com/