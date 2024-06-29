# INSTALLATION of SCANS
I will present the configuration and usage of SCANS with a practical example of setting up a monitoring module and one general spectrometer module on separate machines, both running an x86 lightweight Linux OS (lubuntu) with Python 3.10.12. By default, SCANS' containers refer to x86-specific containers. You may run into issues when attempting to configure SCANS on older 32-bit madchines, ARM, or Apple silicon. Specific containers do exist for these architectures, but they may require more advanced configuration.

If you are coming from the NMR world, where x86 CentOS 5/7 are common place, the default containers should be sufficient. 


### Basic configuration

The only prerequistes for SCANS are the programs 'docker' and 'docker-compose'. Some Linux operating systems come with these by default and the setup.py script will warn you if these programs are not installed (or cannot be found). If you need to install them, run:

For Ubuntu-based systems:
```
sudo apt update
sudo apt install docker.io docker-compose
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
- ask you what module you would like to configure (for now, just script is limited to spectrometer and monitor modules)
- ask you to define an short name for your computer

** I should add a check for '--version', not just that the files are present

 
### The Monitoring module

The main SCANS package can be downloaded with the following command:  
wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip

Unpack and move into the monitoring directory
unzip main.zip
mv main SCANS  
cd SCANS/Modules/Monitor




BE SURE TO MENTION OPENING THE PORTS! 
he fully customizable if they overlap with any existing service. 