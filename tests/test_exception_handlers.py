
import pytest

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.main import (
    tratar_erro_inesperado,
    tratar_erro_validacao,
    tratar_http_exception,
)


@pytest.fixture
def client():
    app = FastAPI()

    app.add_exception_handler(
        HTTPException,
        tratar_http_exception,
    )
    app.add_exception_handler(
        RequestValidationError,
        tratar_erro_validacao,
    )
    app.add_exception_handler(
        Exception,
        tratar_erro_inesperado,
    )

    @app.get("/http-error")
    async def http_error():
        raise HTTPException(
            status_code=403,
            detail="Acesso negado.",
        )

    @app.get("/unexpected-error")
    async def unexpected_error():
        raise RuntimeError("detalhe interno secreto")

    @app.get("/validate")
    async def validate(value: int):
        return {"value": value}

    return TestClient(app, raise_server_exceptions=False)


def test_preserva_status_http(client):
    response = client.get("/http-error")

    assert response.status_code == 403
    assert response.json() == {"detail": "Acesso negado."}


def test_erro_inesperado_retorna_mensagem_generica(client):
    response = client.get("/unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Erro interno do servidor."
    }
    assert "detalhe interno secreto" not in response.text


def test_erro_de_validacao_preserva_422(client):
    response = client.get("/validate?value=abc")

    assert response.status_code == 422
    assert "detail" in response.json()

    for erro in response.json()["detail"]:
        assert "input" not in erro