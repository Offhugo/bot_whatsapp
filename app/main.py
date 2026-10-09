
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.webhook import router as webhook_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Bot API")


@app.exception_handler(HTTPException)
async def tratar_http_exception(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    if exc.status_code >= 500:
        logger.error(
            "Erro HTTP %s na rota %s",
            exc.status_code,
            request.url.path,
        )
    else:
        logger.warning(
            "Requisição recusada: HTTP %s na rota %s",
            exc.status_code,
            request.url.path,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Falha de validação na rota %s",
        request.url.path,
    )

    # Não retornamos "input" nem o corpo recebido:
    # eles podem conter dados privados do usuário.
    erros = [
        {
            "loc": erro.get("loc"),
            "msg": erro.get("msg"),
            "type": erro.get("type"),
        }
        for erro in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": erros},
    )


@app.exception_handler(Exception)
async def tratar_erro_inesperado(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Erro inesperado na rota %s",
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor."
        },
    )


app.include_router(webhook_router)