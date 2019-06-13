FROM ubuntu:latest
#FROM alpine:latest
# Update OS
RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade

# Install Python
#RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y python3 python3-pip python3-dev python3-setuptools
# https://stackoverflow.com/questions/21669354/rebuild-uwsgi-with-pcre-support
RUN apt-get install -y libpcre3 libpcre3-dev
RUN pip3 install --upgrade pip
RUN pip install --upgrade pip


# Add requirements.txt
# Create app directory
ADD   /src /app

# Install wsgi Python web server
RUN pip3 install uwsgi
# Install app requirements
# Full path to requirements
RUN pip3 install -r /app/requirements.txt

RUN apt-get update
RUN apt-get -y upgrade

# Set the default directory for our environment
ENV HOME /app
WORKDIR /app

# Expose port 8000 for uwsgi
EXPOSE 8000

# "--uid", "uwsgi"
ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--module", "app:app", "--processes", "2", "--threads", "8"]




