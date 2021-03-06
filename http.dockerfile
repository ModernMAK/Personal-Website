FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 80

# Setup App
WORKDIR /webserver
COPY requirements.txt .
COPY ./src .
RUN pip install -r requirements.txt

# Setup NGinx
WORKDIR /nginx-conf
RUN apt-get update -y
RUN apt-get install nginx -y
COPY ./nginx/http.conf .

# Startup, run nginx and uvicorn
WORKDIR /
CMD /bin/bash -c " nginx -c /nginx-conf/http.conf; cd webserver; uvicorn app:web_app --host 0.0.0.0 --port 8080 --uds /uvicorn.sock --log-level debug;"
#  ls; cd /var/log/nginx; ls; cat access.log; cat error.log;
