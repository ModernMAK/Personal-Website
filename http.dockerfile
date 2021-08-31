FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 80 443

# Setup NGinx
RUN apt-get update -y
RUN apt-get install nginx -y

WORKDIR /nginx-conf
copy ./nginx/http.conf .


# Setup App
WORKDIR /website
COPY requirements.txt .
COPY ./src .
RUN pip install -r requirements.txt

WORKDIR /
CMD ["uvicorn", "/website/app:web_app", "--host", "0.0.0.0", "--port", "8080", --uds /uvicorn.sock]
