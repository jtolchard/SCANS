#!/bin/bash
# Setup script for configuring and running SCANS containers
#
# JT - 15.04.2023
#
#Points

#2 Ask what kind of configuration you want!
# Print a header


echo "
___________________________________
  ____   ____    _    _   _ ____  
 / ___| / ___|  / \  | \ | / ___| 
 \___ \| |     / _ \ |  \| \___ \ 
  ___) | |___ / ___ \| |\  |___) |
 |____/ \____/_/   \_\_| \_|____/ 
 
       SCANS CONTAINER SETUP 
___________________________________
"

# Check for necessary packages
if ! command -v docker &> /dev/null
then
    echo "Docker was not found within the system paths. Please install it to proceed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose was not found within the system paths. Please install it to proceed."
    exit 1
fi

if ! command -v git &> /dev/null
then
    echo "git was not found within the system paths. It's installation is recommended to streamline deployment."
fi
#Ask user for type of installation
echo " Which SCANS module do you want to setup?:
    Spectrometer Logging    [1]
    Server/RAID Logging     [2]
    Monitoring System & DBs [3]
     "

## Read user choice
read -p "Choice: " answer
#if [ "$answer" != "1" ] || [ "$answer" != "2" ]; then
if [ "$answer" != "1" ] && [ "$answer" != "2" ] && [ "$answer" !=  "3" ]; then
  echo "invalid response"
  exit 1
fi

#Setup for spectromeer logging container
if [ "$answer" == "1" ]; then
  echo "Setting up Spectrometer Logging Module"

## Ask user for spectrometer name
count=0
while [ $count -ne 1 ]
do
  read -p "Choose a spectrometer name: " spect_name
  read -p "Set name to $spect_name? (y/n): " chk
  if [ "$chk" == "y" ]; then
    count=1
  fi
done
#Setup for server logging container
elif [ "$answer" == "2" ]; then
  echo "Setting up Server/RAID Logging module"
#Setup for monitoring container
elif [ "$answer" == "3" ]; then
  echo "Setting up Monitoring System & Logging Databases"
fi