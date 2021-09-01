FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 

# Setup App
COPY ../requirements.txt .
COPY ../src .
RUN pip install -r requirements.txt

# Startup uvicorn ~ must mount /sockets
CMD ["uvicorn", "app:web_app", "--uds", "/sockets/website-dev.sock"]
