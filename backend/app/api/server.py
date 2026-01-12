import logging

from app.api.middleware import RequestLoggingMiddleware
from app.api.v1.routes import router as api_router
from app.core import config
from app.core.logging_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("anonify")

def get_application():
    logger.info("Starting application.")
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=config.API_PREFIX)

    return app


setup_logging()
app = get_application()
