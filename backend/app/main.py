import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.responses import JSONResponse, Response
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION

try:
    # fastapi-limiter has multiple variants in the wild; some do not expose errors.RateLimitExceeded.
    from fastapi_limiter.errors import RateLimitExceeded  # type: ignore
except Exception:  # pragma: no cover
    RateLimitExceeded = None  # type: ignore

setup_logging()

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


@app.on_event("startup")
async def setup_rate_limiter():
    if not settings.rate_limit_enabled:
        return
    redis_url = settings.rate_limit_redis_url or settings.redis_url
    if not redis_url:
        return
    try:
        redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis)
        logger.info("rate_limiter_ready")
    except Exception:
        # Graceful degradation: allow API to start even if rate limiting backend is unavailable.
        logger.exception("rate_limiter_init_failed", extra={"redis_url": redis_url})


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    start = time.perf_counter()
    request_id = request.headers.get("x-request-id") or uuid4().hex
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        response = None
        raise
    finally:
        duration = time.perf_counter() - start
        duration_ms = int(duration * 1000)
        # Reduce Prometheus label cardinality: prefer route templates (e.g. /v1/channels/{channel_id})
        # over the raw URL path (e.g. /v1/channels/123).
        route = request.scope.get("route")
        path_label = getattr(route, "path", None) or request.url.path
        if response is not None:
            response.headers.setdefault("X-Request-ID", request_id)
        if settings.metrics_enabled and request.url.path != "/metrics":
            status_code = str(response.status_code) if response is not None else "500"
            HTTP_REQUESTS_TOTAL.labels(request.method, path_label, status_code).inc()
            HTTP_REQUEST_DURATION.labels(request.method, path_label).observe(duration)
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "path_label": path_label,
                "status_code": response.status_code if response is not None else 500,
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


if RateLimitExceeded is not None:
    @app.exception_handler(RateLimitExceeded)  # type: ignore[arg-type]
    async def rate_limit_handler(request: Request, exc):  # noqa: ANN001
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests", "request_id": request_id},
            headers={"X-Request-ID": request_id} if request_id else None,
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    if not settings.metrics_enabled:
        return Response(status_code=404)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
