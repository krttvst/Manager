import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.responses import JSONResponse, Response
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title="Manager TG API", version="0.1.0")
logger = logging.getLogger("manager_tg")

app.include_router(api_router)
Path(settings.media_dir).mkdir(parents=True, exist_ok=True)


class MediaStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code == 404 and path.startswith("previews/"):
            response = await super().get_response(path[len("previews/"):], scope)
        if response.status_code == 200:
            response.headers.setdefault("Cache-Control", "public, max-age=31536000, immutable")
        return response


app.mount("/media", MediaStaticFiles(directory=settings.media_dir), name="media")


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    start = time.perf_counter()
    request_id = request.headers.get("x-request-id") or uuid4().hex
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers.setdefault("X-Request-ID", request_id)
    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
        headers={"X-Request-ID": request_id} if request_id else None,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_error", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "request_id": request_id},
        headers={"X-Request-ID": request_id} if request_id else None,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
