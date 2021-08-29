FROM python:3.8.1-slim

ENV PYTHONUNBUFFERED 1 

EXPOSE 8080

WORKDIR /app

COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt

CMD ["uvicorn", "app:web_app", "--host", "0.0.0.0", "--port", "8080"]