from fastapi import APIRouter

router = APIRouter()


@router.get("/", name="ping")
async def ping():
    return {"message": "pong"}
