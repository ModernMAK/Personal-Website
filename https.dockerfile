FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 8443

# Setup App
COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt

CMD ["uvicorn", "app:web_app", "--ssl-keyfile", "/etc/letsencrypt/live/development.modernmak.com/privkey.pem", "--ssl-certfile", "/etc/letsencrypt/live/development.modernmak.com/fullchain.pem", "--host", "0.0.0.0", "--port", "8443"]
