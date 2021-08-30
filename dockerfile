FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 8080
WORKDIR /app

# Setup App
COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt

# Setup Cert-Bot
# 	Assuming linux distro
# RUN sudo yum install python3 augeas-libs
#	Remove old certbot if present
# RUN sudo yum remove certbot
RUN python3 -m venv /venv/certbot/
RUN /venv/certbot/bin/pip install --upgrade pip
RUN /venv/certbot/bin/pip install certbot
# RUN /ln -s /venv/certbot/bin/certbot /usr/bin/certbot

RUN /venv/certbot/bin/certbot --help


CMD ["uvicorn", "app:web_app", "--host", "0.0.0.0", "--port", "8080"]