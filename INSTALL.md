<img width="1834" alt="banner" src="https://github.com/jtolchard/SCANS/assets/50239502/45bbe5c9-82d0-41dd-93d6-5766a50159d7">

# SCANS
I will present the configuration and usage of SCANS with a practical example of setting up a monitoring module and one general spectrometer module on separate machines, both running an x86 lightweight Linux OS (lubuntu). By default, SCANS' containers refer to x86-specific containers. You may run into issues when attempting to configure SCANS on older 32-bit madchines, ARM, or Apple silicon. Specific containers to exist for these architectures, but they may require more advanced configuration.

If you are coming from the NMR world, where x86 CentOS 5/7 are common place, the default containers should be sufficient. Just keep in mind any "sudo apt install" commands noted below will instead be "sudo yum install" on CentOS.


## INSTALLATION of SCANS
The main SCANS package can be downloaded with the following command:  
wget https://github.com/jtolchard/SCANS/archive/refs/heads/main.zip