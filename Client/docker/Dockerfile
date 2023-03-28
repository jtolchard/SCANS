# Dockerfile to create image with cron services
FROM ubuntu:18.04
#FROM python:latest  #To consider for the future when stripped down!

# Add the script to the Docker Image
ADD ../scraper.py /root/scans/scraper.py
ADD ../clientparams.py /root/scans/clientparams.py

# Give execution rights on the cron scripts
RUN chmod 0644 /root/scans/scraper.py

#Install Cron
RUN apt-get update
RUN apt-get -y install vim python3

#Set the working directory
WORKDIR /root/scans/

# Run the command on container startup
#CMD /usr/bin/python3 scraper.py --output-file ./logs/OUTPUT/demo_output.txt
CMD /bin/bash