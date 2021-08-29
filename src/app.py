from fastapi import FastAPI
from main import setup
web_app = FastAPI(openapi_url=None)  # disable docs; not a rest-api but a webserver
setup(web_app)