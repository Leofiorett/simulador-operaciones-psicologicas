from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health", tags=["infra"])
async def health():
    return {"status": "ok", "servicio": "sop-backend", "version": "1.0.0"}
