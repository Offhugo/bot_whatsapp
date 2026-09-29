import hashlib
import hmac

from app.utils.meta_webhook_security import (
    verificar_token_meta,
    verificar_assinatura_meta
)


def test_token_meta_valido(monkeypatch):
    # Define o token esperado pela aplicação.
    monkeypatch.setenv(
        "META_VERIFY_TOKEN",
        "token-teste"
    )

    assert verificar_token_meta(
        "token-teste"
    )


def test_token_meta_invalido(monkeypatch):
    # Define o token esperado pela aplicação.
    monkeypatch.setenv(
        "META_VERIFY_TOKEN",
        "token-teste"
    )

    assert not verificar_token_meta(
        "token-errado"
    )


def test_assinatura_meta_valida(monkeypatch):
    # Simula o App Secret configurado na Meta.
    app_secret = "app-secret-teste"

    monkeypatch.setenv(
        "META_APP_SECRET",
        app_secret
    )

    payload = b'{"object":"whatsapp_business_account"}'

    digest = hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    assinatura = f"sha256={digest}"

    assert verificar_assinatura_meta(
        payload,
        assinatura
    )


def test_assinatura_meta_invalida(monkeypatch):
    # Define o App Secret correto.
    monkeypatch.setenv(
        "META_APP_SECRET",
        "app-secret-teste"
    )

    payload = b'{"object":"whatsapp_business_account"}'

    assinatura_falsa = (
        "sha256="
        "assinatura-completamente-falsa"
    )

    assert not verificar_assinatura_meta(
        payload,
        assinatura_falsa
    )


def test_assinatura_meta_ausente(monkeypatch):
    # Mesmo com o App Secret configurado,
    # a ausência da assinatura deve resultar em falha.
    monkeypatch.setenv(
        "META_APP_SECRET",
        "app-secret-teste"
    )

    payload = b'{"object":"whatsapp_business_account"}'

    assert not verificar_assinatura_meta(
        payload,
        None
    )