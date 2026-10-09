
import logging
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.api_version = os.getenv("WHATSAPP_API_VERSION")

    async def enviar_mensagem(self, telefone: str, mensagem: str):
        if not self.access_token:
            raise RuntimeError("WHATSAPP_ACCESS_TOKEN não configurado.")

        if not self.phone_number_id:
            raise RuntimeError("WHATSAPP_PHONE_NUMBER_ID não configurado.")

        if not self.api_version:
            raise RuntimeError("WHATSAPP_API_VERSION não configurado.")

        url = (
            f"https://graph.facebook.com/"
            f"{self.api_version}/{self.phone_number_id}/messages"
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": mensagem,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.warning(
                "Timeout ao enviar mensagem pela API do WhatsApp."
            )
            raise

        except httpx.ConnectError:
            logger.error(
                "Falha de conexão com a API do WhatsApp."
            )
            raise

        except httpx.HTTPStatusError as exc:
            logger.error(
                "API do WhatsApp respondeu com status HTTP %s.",
                exc.response.status_code,
            )
            raise