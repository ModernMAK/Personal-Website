import json
from typing import Dict, List, Optional

import pystache
import uvicorn as uvicorn
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles


def setup(app: FastAPI) -> None:
    """
    Initializes all routes required by the website. By containing it in a function, I can control when routes are added, which allows me to reuse routes.

    :param app: The fast api instance to initialize with the website
    """

    # Initialize Pystache
    renderer = pystache.Renderer(search_dirs="static/templates")
    # Initialize IMG and CSS, the only two static directories we expose
    #   HTML & templates are managed by routes
    app.mount("/img", StaticFiles(directory="static/img"))
    app.mount("/css", StaticFiles(directory="static/css"))

    # Open configurations; projects & buzzwords
    with open("data/projects.json") as j_file:
        projects = json.load(j_file)

    with open("data/buzzwords.json") as j_file:
        buzzwords = json.load(j_file)

    # Cleanup buzzwords
    for key, value in buzzwords.items():
        if 'name' not in value:
            value['name'] = key
        if 'alias' in value:
            spaced = [n.replace(" ", "-") for n in value['alias'] if " " in n]
            value['alias'].extend(spaced)
        if 'safe_name' not in value:
            value['safe_name'] = value['name']

    # Helper to get a buzzword from a word; uses aliases, safe_name, and key
    def get_buzz_from_dict(word: str, buzz: Dict = None) -> Optional[Dict]:
        buzz = buzz or buzzwords

        if word in buzz:
            return buzz[word]

        word = word.lower()
        for key, value in buzz.items():
            if key.lower() == word:
                return value
            if 'safe_name' in value:
                if word == value['safe_name'].lower():
                    return value

            if 'alias' in value:
                for a in value['alias']:
                    if a.lower() == word:
                        return value
        return None

    def get_buzz_from_list(word: str, buzz: List) -> Optional[Dict]:
        if buzz is None:
            return None
        else:
            d = {b['name']: b for b in buzz}
            return get_buzz_from_dict(word, d)

    def project_has_buzz(project: Dict, word: str) -> bool:
        return get_buzz_from_list(word, project.get("buzzword", None)) is not None

    for project in projects:
        project['sub_url'] = f"/projects/{project['id']}"
        if 'description' in project:
            desc = project['description']
        elif 'description_file' in project:
            with open(project['description_file'], "r") as f:
                desc = f.read()
        else:
            try:
                with open(f"data/descriptions/{project['id']}.txt", "r") as f:
                    desc = f.read()
            except FileNotFoundError:
                desc = None
        if desc is not None:
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
            tag_buzz = get_buzz_from_dict(tag)
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
    uvicorn.run(web_app, port=80, host="127.0.0.1")
