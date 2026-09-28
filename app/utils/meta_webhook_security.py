import hashlib
import hmac
import os


def verificar_token_meta(
    verify_token: str | None
) -> bool:
    """
    Verifica o token enviado pela Meta durante
    o handshake de configuração do webhook.
    """

    token_esperado = os.getenv("META_VERIFY_TOKEN")

    if not token_esperado or not verify_token:
        return False

    return hmac.compare_digest(
        verify_token,
        token_esperado
    )


def verificar_assinatura_meta(
    payload: bytes,
    assinatura: str | None
) -> bool:
    """
    Verifica a assinatura HMAC-SHA256 enviada pela Meta.

    A assinatura é calculada sobre o corpo bruto
    da requisição usando o App Secret da aplicação.
    """

    app_secret = os.getenv("META_APP_SECRET")

    if not app_secret or not assinatura:
        return False

    prefixo = "sha256="

    if not assinatura.startswith(prefixo):
        return False

    assinatura_esperada = (
        prefixo
        + hmac.new(
            app_secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
    )

    return hmac.compare_digest(
        assinatura_esperada,
        assinatura
    )