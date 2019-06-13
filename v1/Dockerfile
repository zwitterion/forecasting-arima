#FROM salesgraph.azurecr.io/python-base:v1
FROM python-base:latest

RUN  apt-get update 
RUN  apt-get install -y wget 
#RUN  apt-get install -y bash

COPY  src /app/

# Install app requirements
RUN pip3 install -r /app/requirements.txt

# Set the default directory for our environment
ENV HOME /app
WORKDIR /app

# Without PYTHONUNBUFFERED=0 kubernetest logs won't be visible
ENV PYTHONUNBUFFERED=0
ENV PYTHONIOENCODING=UTF-8

# "./trainer.py"
ENTRYPOINT ["python3"] 
