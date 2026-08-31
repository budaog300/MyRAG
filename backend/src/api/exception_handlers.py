import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from src.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    logger.error(f"Domain Exception при вызове {request.method} [{exc.__class__.__name__}]: {exc.message}", exc_info=True)
    response_content = {"detail": exc.message}
    if exc.extra:
        response_content["extra"] = exc.extra

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Необработанная ошибка при вызове {request.method} {request.url.path}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера. Обратитесь к администратору."},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)