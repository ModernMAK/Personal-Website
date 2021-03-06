FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 80 443

# Setup App
WORKDIR /webserver
COPY requirements.txt .
COPY ./src .
RUN pip install -r requirements.txt

# Setup NGinx
WORKDIR /nginx-conf
RUN apt-get update -y
RUN apt-get install nginx -y
COPY ./nginx/https-dev.conf .

# Startup, run nginx and uvicorn
WORKDIR /
CMD /bin/bash -c " nginx -c /nginx-conf/https-dev.conf; cd webserver; uvicorn app:web_app --host 0.0.0.0 --port 8080 --uds /uvicorn.sock --log-level debug; cd /var/log/nginx; echo Opening access.log; cat access.log; echo Opening error.log; cat error.log;"
