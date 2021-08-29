# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css
# https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.min.js
#
import json
import os
from typing import Dict, List, Optional

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
        if 'alias' in value:
            spaced = [n.replace(" ", "-") for n in value['alias'] if " " in n]
            value['alias'].extend(spaced)
        if 'safe_name' not in value:
            value['safe_name'] = value['name']

    def get_buzz(word: str) -> Optional[Dict]:
        if word in buzzwords:
            return buzzwords[word]

        word = word.lower()
        for key, value in buzzwords.items():
            if key.lower() == word:
                return value
            if 'alias' in value:
                for a in value['alias']:
                    if a.lower() == word:
                        return value
        return None

    def project_has_buzz(project: Dict, word: str) -> bool:
        word = word.lower()

        for buzz in project['buzzwords']:
            if word == buzz['name'].lower():
                return True
            if 'alias' in buzz:
                for a in buzz['alias']:
                    if word == a.lower():
                        return True
        return False

    for project in projects:
        project['sub_url'] = f"/projects/{project['id']}"
        desc = project['description']
        project['lines'] = [{'line': part} for part in desc.split("\n") if len(part) > 0]
        buzz: List = project.get('buzzwords', None)
        if buzz:
            buzz.sort()

            for b in buzz:
                if b not in buzzwords:
                    buzzwords[b] = {'name': b}

            project['buzzwords'] = [buzzwords[b] for b in buzz]
            project['has_buzzwords'] = True

    project_lookup = {project['id']: project for project in projects}

    @app.get("/")
    def index_page():
        return RedirectResponse(url="/projects")

    @app.get("/projects")
    def project_index_page(tag: str = None):
        local_projects = projects
        ctx = {}
        if tag:
            ctx['tag'] = {'name': tag}
            tag_buzz = get_buzz(tag)
            if tag_buzz is not None:
                ctx['info'] = tag_buzz
                local_projects = [p for p in local_projects if project_has_buzz(p, tag)]
                if len(local_projects) == 0:
                    ctx['tag']['warn_proj'] = True
            else:
                ctx['tag']['warn_tag'] = True

        ctx['projects'] = local_projects
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
    try:

        # for cdir, _, files in os.walk("/"):
        #     print(cdir)
        #     for f in files:
        #         print("\t", os.path.join(cdir,f))

        key = "/etc/letsencrypt/live/development.modernmak.com/privkey.pem"
        cert = "/etc/letsencrypt/live/development.modernmak.com/fullchain.pem"

        for root, folders, files in os.walk("/etc/letsencrypt/live/development.modernmak.com"):
            print(root)
            for f in folders:
                f_path = os.path.join(root, f)
                print("DIR", "\t", f, "\t", os.path.exists(f_path), "\t", os.access(f_path, os.R_OK), "\t", os.access(f_path, os.W_OK), "\t", os.access(f_path, os.X_OK))
            for f in files:
                f_path = os.path.join(root, f)
                print("FILE", "\t", f, "\t", os.path.exists(f_path), "\t", os.access(f_path, os.R_OK), "\t", os.access(f_path, os.W_OK), "\t", os.access(f_path, os.X_OK))

        print()
        print("KEY")
        c = key
        for i in range(5):  # while true but safer
            print("\t", c, ":", os.path.exists(c))
            c = os.path.dirname(c)
            if c in ["/", ""]:
                break

        print("CERT")
        c = cert
        for i in range(5):  # while true but safer
            print("\t", c, ":", os.path.exists(c))
            c = os.path.dirname(c)
            if c in ["/", ""]:
                break

        print(os.stat(key))
        print(os.stat(cert))

        with open(key, "r") as _:
            pass
        with open(cert, "r") as _:
            pass
        uvicorn.run(web_app, ssl_keyfile=key, ssl_certfile=cert, port=8080, host="0.0.0.0")
    except FileNotFoundError as e:
        print(e.errno, e.filename, *e.args)
        raise e
