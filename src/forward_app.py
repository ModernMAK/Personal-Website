from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

fwd_app = FastAPI(openapi_url=None)  # disable docs; not a rest-api but a webserve
HTTP = "http"
HTTPS = "https"
MOVED_PERM = 301
NOT_FOUND = 404


def forward_request(request: Request):
    if HTTP in request.url.scheme:
        url = request.url.replace(scheme=HTTPS)
        return RedirectResponse(url=url, status_code=MOVED_PERM, headers=request.headers)
    return HTTPException(NOT_FOUND, "The url is not using HTTP!")


@fwd_app.get("/")
def forward_root_to_https(request: Request):
    return forward_request(request)


@fwd_app.get("/{full_path}")
def forward_path_to_https(request: Request, full_path: str):
    return forward_request(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fwd_app, port=80, host="127.0.0.1")
