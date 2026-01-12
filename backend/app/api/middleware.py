import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("anonify.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()

        # Extract request information
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else None

        # Log request
        logger.info(
            f"Request: {method} {path}",
            extra={
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_host": client_host,
                "client_port": client_port,
                "request_id": request.headers.get("X-Request-ID", None),
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time

            # Log error
            logger.error(
                f"Request failed: {method} {path}",
                exc_info=True,
                extra={
                    "method": method,
                    "path": path,
                    "process_time": round(process_time, 4),
                    "status_code": 500,
                    "error": str(e),
                },
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Extract response information
        status_code = response.status_code

        # Log response
        log_level = logging.INFO if status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            f"Response: {method} {path} - {status_code}",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "process_time": round(process_time, 4),
                "client_host": client_host,
            },
        )

        return response
