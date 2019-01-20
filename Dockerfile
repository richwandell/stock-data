FROM ubuntu:latest

COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y python3-pip libfreetype6-dev vim nodejs npm
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
RUN pip3 install --upgrade setuptools
RUN pip3 install freetype-py
RUN pip3 install pypng
RUN pip3 install -r requirements.txt
RUN npm install -g grunt-cli

RUN touch /var/log/app.log