from app.api.v1.routes.pii_remover import router as pii_remover_router
from app.api.v1.routes.ping import router as ping_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(ping_router, prefix="/ping", tags=["ping"])
router.include_router(pii_remover_router, prefix="/pii", tags=["pii"])
