from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

fwd_app = FastAPI(openapi_url=None)  # disable docs; not a rest-api but a webserve
HTTP = "http"
HTTPS = "https"
MOVED_PERM = 301
NOT_FOUND = 404
UNAUTHORIZED = 401


def forward_request(request: Request):
    if HTTP in request.url.scheme:
        url = request.url.replace(scheme=HTTPS)
        return RedirectResponse(url=url, status_code=MOVED_PERM, headers=request.headers)
    return HTTPException(NOT_FOUND, "The url is not using HTTP!")


def block_request(request: Request):
    return HTTPException(UNAUTHORIZED, "The url requires an HTTPS connection!")


@fwd_app.get("/")
def forward_root_to_https(request: Request):
    return forward_request(request)


@fwd_app.get("/{full_path}")
def forward_path_to_https(request: Request, full_path: str):
    return forward_request(request)


@fwd_app.post("/")
@fwd_app.patch("/")
@fwd_app.put("/")
@fwd_app.delete("/")
def block_root_to_https(request: Request):
    return block_request(request)


@fwd_app.patch("/{full_path}")
@fwd_app.put("/{full_path}")
@fwd_app.delete("/{full_path}")
@fwd_app.get("/{full_path}")
def block_path_to_https(request: Request, full_path: str):
    return block_request(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fwd_app, port=80, host="127.0.0.1")
