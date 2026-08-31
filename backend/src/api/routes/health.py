from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from src.api.deps import HealthCheckDep

router = APIRouter(prefix="/health", tags=["System"])


class HealthResponseSchema(BaseModel):
    status: str
    services: dict[str, bool]


@router.get(
    "",
    response_model=HealthResponseSchema,
    summary="Проверка доступности зависимостей (Healthcheck)",
)
async def health_check(
    response: Response,
    health_service: HealthCheckDep,
):
    result = await health_service.run_all_checks()

    if result["status"] != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return result