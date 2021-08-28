# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css
# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.min.js
#
import json

import pystache
import uvicorn as uvicorn
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles


def main(app):
    renderer = pystache.Renderer(search_dirs="static/templates")
    app.mount("/img", StaticFiles(directory="static/img"))
    with open("data/projects.json") as j_file:
        projects = json.load(j_file)

    @app.get("/")
    def project_index_page():
        ctx = {'projects': projects}
        content = renderer.render_path("static/html/project_index.html", **ctx)
        return HTMLResponse(content)

    for project in projects:
        def wrapper(url, html_path):
            @app.get(url)
            def project_page():
                ctx = {}
                content = renderer.render_path(html_path, **ctx)
                return HTMLResponse(content)
        wrapper(project.get('sub_url',None), project.get('html_path',None))


if __name__ == "__main__":
    web_app = FastAPI()
    main(web_app)
    uvicorn.run(web_app)
