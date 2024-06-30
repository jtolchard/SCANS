FROM python:3.7

#install all necessary libraries
RUN apt-get update 
RUN apt-get install -y apt-utils libgbm1 gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils libu2f-udev vim cron

#install python dependencies
COPY requirements.txt requirements.txt 
RUN /usr/local/bin/python -m pip install --upgrade pip
#RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt 

#setup cron
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

#manage local files
WORKDIR /app
COPY . .
RUN mkdir /app/logs
RUN mkdir /app/setup
RUN mv requirements.txt /app/setup/
RUN mv crontab /app/setup/
RUN mv Dockerfile /app/setup

#set time zone
ENV TZ="Europe/Paris"

CMD ["cron", "-f"]