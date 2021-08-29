# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css
# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.min.js
#
import json
from typing import Dict, List

import pystache
import uvicorn as uvicorn
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles


def setup(app):
    renderer = pystache.Renderer(search_dirs="static/templates")
    app.mount("/img", StaticFiles(directory="static/img"))
    app.mount("/css", StaticFiles(directory="static/css"))
    with open("data/projects.json") as j_file:
        projects = json.load(j_file)

    with open("data/buzzwords.json") as j_file:
        buzzwords = json.load(j_file)

    for key, value in buzzwords.items():
        if 'name' not in value:
            value['name'] = key

    for project in projects:
        project['sub_url'] = f"/projects/{project['id']}"
        desc = project['description']
        project['lines'] = [{'line': part} for part in desc.split("\n") if len(part) > 0]
        buzz: List = project.get('buzzwords', None)
        if buzz:
            buzz.sort()

            def default_buzz(word: str) -> Dict:
                return {'name': word}

            project['buzzwords'] = [buzzwords.get(b, default_buzz(b)) for b in buzz]
            project['has_buzzwords'] = True

    project_lookup = {project['id']: project for project in projects}

    @app.get("/")
    def index_page():
        return RedirectResponse(url="/projects")

    @app.get("/projects")
    def project_index_page():
        ctx = {'projects': projects}
        content = renderer.render_path("static/html/project_index.html", **ctx)
        return HTMLResponse(content)

    @app.get("/projects/{project_id}")
    def project_page(project_id: str):
        if project_id not in project_lookup:
            raise HTTPException(404)
        project = project_lookup[project_id]
        ctx = project
        content = renderer.render_path("static/html/project_page.html", **ctx)
        return HTMLResponse(content)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        allowed = [301, 303, 307, 400, 404, 410, 418]

        if exc.status_code not in allowed:
            print("Uncaught")
            raise exc

        html = renderer.render_path(f"static/html/error/{exc.status_code}.html")
        return HTMLResponse(content=html, status_code=exc.status_code)


if __name__ == "__main__":
    web_app = FastAPI(openapi_url=None)  # disable docs; not a rest-api but a webserver
    setup(web_app)
    uvicorn.run(web_app, port=8080, host="127.0.0.1")
