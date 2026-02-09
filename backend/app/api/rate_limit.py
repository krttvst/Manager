import logging

from fastapi import Request, Response
from fastapi_limiter.depends import RateLimiter

from app.core.config import settings

logger = logging.getLogger("rate_limit")


def optional_rate_limiter(*, times: int, seconds: int):
    """
    Best-effort rate limiting.

    If Redis/fastapi-limiter is not initialized (or fails), we allow the request
    to proceed instead of returning 500. This matches the project's
    "graceful degradation" intent.
    """

    async def _dep(request: Request, response: Response) -> None:
        if not settings.rate_limit_enabled:
            return
        if not getattr(request.app.state, "rate_limiter_ready", False):
            return

        limiter = RateLimiter(times=times, seconds=seconds)
        try:
            # fastapi-limiter variants differ in call signature; try common forms.
            try:
                await limiter(request, response)  # type: ignore[misc]
            except TypeError:
                await limiter(request)  # type: ignore[misc]
        except Exception:
            logger.exception(
                "rate_limit_failed",
                extra={"path": request.url.path, "times": times, "seconds": seconds},
            )

    return _dep

