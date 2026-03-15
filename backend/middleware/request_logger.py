import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("cvmatch.requests")

class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s | %d | %.0fms | %s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request.client.host
        )

        return response