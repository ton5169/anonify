from app.api.v1.routes.ping import router as ping_router
from app.api.v1.routes.sanitizer import router as sanitizer_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(ping_router, prefix="/ping", tags=["ping"])
router.include_router(sanitizer_router, prefix="/sanitizer", tags=["sanitizer"])
