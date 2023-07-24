FROM python:3.7

#install all necessary libraries
RUN apt-get update
RUN apt-get install exim4-base exim4-config exim4-daemon-light gsasl-common guile-2.2-libs libgc1 libgnutls-dane0 libgpm2 libgsasl7 libidn11 libmailutils7 libntlm0 libpython3.9 libunbound8 mailutils mailutils-common psmisc vim-common vim-runtime xxd vim cron

#install python dependencies
COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
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
