# INSTALLATION of SCANS
I will present the configuration and usage of SCANS with a practical example of setting up a monitoring module and one general spectrometer module on separate machines, both running an x86 lightweight Linux OS (lubuntu) with Python 3.10.12. By default, SCANS' containers refer to x86-specific containers. You may run into issues when attempting to configure SCANS on older 32-bit madchines, ARM, or Apple silicon. Specific containers do exist for these architectures, but they may require more advanced configuration.

If you are coming from the NMR world, where x86 CentOS 5/7 are common place, the default containers should be sufficient. 


### Basic configuration

The only prerequistes for SCANS are the programs 'docker' and 'docker-compose'. Some Linux operating systems come with these by default and the setup.py script will warn you if these programs are not installed (or cannot be found). If you need to install them, run:

For Ubuntu-based systems:
```
sudo apt update
sudo apt install docker docker-compose
```
For RedHat-based systems (including CentOS):
```
sudo yum update 
sudo yum install docker docker-compose
```

Regardless of your OS, you will then need to start the Docker service and enable it at boot:
```
sudo systemctl start docker
sudo systemctl enable docker
```

that's it...

Installers and installation information for Mac and Windows (WSL) can be found [here](https://docs.docker.com/compose/install/)


### The SCANS repository

The main SCANS package can be downloaded with the following command:  
wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip

Unpack and move into the main directory
```
unzip main.zip
mv main SCANS  
cd SCANS
```

This directory needs to exist on every computer that will run a module. The module configurations, log files, and databases will be stored here - so make sure the location is future-proof and secure. You will need to run the setup script with elevated permissions (sudo/root).

### The Client modules: Spectrometer logging

For a first installation, I recommend you configure, start, and test your desired client modules (on each machine) before moving on to the main monitoring module. This isn't obligatory (the modules function independently), however having all of the aliases and IP addresses for your client machines will simplify setup of the monitoring.

I've created a setup.py script which I hope will cater for most instances of spectrometer logging. Once within the SCANS main directory, you can run the setup with:

```python3 setup.py```  

This will
- check you have elevated permissions
- check you have docker and docker-compose installed
- check you have a local network connection
- ask you what module you would like to configure (for now, the script is limited to spectrometer and monitor modules).

  - Select option 1 for spectrometer logging.
- ask you how your spectrometer logs currently are created.
  This is important, because it defines the location your logs will be read from. 
  If the script can't find these logs in the standard locations, you will be asked for the absolute path to the folder containing the log files.
- the script will then create a configuration file to build the relevant containers and define some configuration files pointing to the correct logs with their formats

The first of these is the docker-compose.yml file. This is what will define all the images for your containers, what they're called, what they can mount on your host system, and how/if they can reach the outside world via the network. The syntax of this file can be quiet complex, but there is plenty of documentation online regarding all the different flags. Importanly, if you require that the services are mapped to different ports, this is the first place to change it.

As for the configuration files, these are used to configure the grok containers which collect specific metrics out of your log files. They need to refer to the intended port, the container-mounted log file, and contain a regex expression which extracts data from every new line. If your files do not conform to standard Bruker formats then you will have to revise these regular expressions. You can find examples of what SCANS expects by default in 'SCANS/Modules/Client-spec/setup/example_logs'. The online tool at https://grokdebugger.com/ can be helpful in creating new expressions.

Once setup for the client is complete, make a note of your alias and IP address (you will need this for for the monitor). You can simply start your new log scraping container with the following commands

```
cd ./Modules/Client-spec
sudo docker-compose up &
```

This will now start your docker containers and they will run indefinitely until the machine is rebooted (I will describe how to start containers at boot time at later.).Once started, the initial output on the console may seem unintelligible, but this is to be expected. It's important to run the 'up' command with an ampersand ('&') to make the command run as a background job. 

If for any reason you wish to stop your containers, you can use the command from the Modules/Client-spec directory
```
sudo docker-compose down
```

For example, containers must be stopped and restarted for any revisions to configuration files to come into effect.

#### - Testing client modules

To test the function and visibility of your containers, you can navigate to: http://<CLIENT_IP_ADDRESS>:9100/metrics in any browser on your network. This will show you the prometheus formatted log information for the computer resource metrics of that workstation. It isn't particularly intuitive, but this is what the future monitoring module will connect to, to retrieve the logs. Aside from port :9100, you can equally choose to look at any module's log information (i.e., 9144 for the helium information) via a browser at any time. However - bear in mind that web pages for spectrometer metrics will only be updated when the log file is updated. Therefore you might have to wait a day for some metrics (i.e,. helium) to refresh. Nonetheless, if you see the webpage for that metric, it should be fine. If the page is simply visible, it`s proof it was configured correctly. If you can't see the web page from other computers, be sure to check your firewall isn't blocking any of the ports SCANS uses (these are outlined on the README page).
 
### <ins>The Monitoring module</ins> 

The monitoring module is also provided in the main SCANS package:  
wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip


Keep in mind, the monitoring module is best installed on a machine that is permanently on and permanently network connected, and the package itself should be stored in a future-proof and secure location, where disk space wont be limiting factor. 

**_NOTE: Importantly, SCANS currently *does not limit database size*, so if unchecked or misconfigured, prometheus can take up all space on the mounted disk._**

Unpack and move into the monitoring directory
unzip main.zip
mv main SCANS  
cd SCANS

Before starting, be sure to have noted all of the IP addresses and aliases for your client containers. The setup.py script also works to configure the monitoring module, so once within the SCANS main directory, you can run the setup with:

```python3 setup.py```  

This will
- check you have elevated permissions
- check you have docker and docker-compose installed
- check you have a local network connection
- ask you what module you would like to configure (for now, the script is limited to spectrometer and monitor modules).

  - Select option 2 for the Monitor module.
- ask you to define a short name for your server
- ask you to define an administrator password for grafana's web interface (but beware, this will be stored as free text in the docker-compose file!)
- the script will then ask you to build a list of your clients and their names. Names can not be blank or contain whitespaces. You will then be prompted to provide an IP address for each machine. This should be the IP address that is shown to you at the end of the client setup. When you have completed your list, just type 'done' in place of a machine name.
- the script will then create a configuration file to build the relevant containers and define some configuration files so the databases look for to collect information from the correct machines.

As before, the first of these is the docker-compose.yml file and defines all the images for your containers, what they're called, what they can mount on your host system, and now, must importantly, the connection details of all your clients.

For the Monitoring module, there are now three configuration files. The first is grafana.ini. This isn't strictly necessary, but I include it for more advanced use cases. In this file, you can provide grafana with addiontional features, such as credentials for sending alerts via email.

The other two files are configuration files for the short and long term prometheus databases (prom-short.yml and prom-long.yml, respectively).










### Additinal Client modules
I currently provide 