FROM python:3.8.1-slim

# Setup Env
ENV PYTHONUNBUFFERED 1 
EXPOSE 8080

# Setup App
COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt

CMD ["uvicorn", "app:web_app", "--host", "0.0.0.0", "--port", "8080"]
