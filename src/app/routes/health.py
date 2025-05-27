from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/", summary="Liveness probe", response_class=JSONResponse)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
