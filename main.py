from fastapi import FastAPI, Request, Response, status
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI(title="WhatsApp Bot API")

# Este token será colocado lá no painel da Meta depois.
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "meutokenmuitoseguro123")


@app.get("/")
def home():
    return {"status": "Bot rodando perfeitamente!"}


# 1. ROTA GET: Verificação da Meta
@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    A Meta vai chamar essa rota uma única vez quando for configurado o webhook no painel deles.
    Eles mandam um 'challenge' (desafio) e é preciso devolver ele pra provar que o servidor é meu.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado com sucesso!")
        # A Meta exige que o challenge seja retornado como texto puro
        return Response(content=challenge, media_type="text/plain")

    # Se o token estiver errado, retorna 403 Forbidden
    return Response(status_code=status.HTTP_403_FORBIDDEN)


# 2. ROTA POST: Receber Mensagens
@app.post("/webhook")
async def receive_message(request: Request):
    """
    Aqui é onde a mágica acontece. Toda vez que alguém mandar msg no Zap, a Meta faz um POST aqui.
    """
    body = await request.json()

    # Imprime no console para vizualizar a estrutura do JSON que a Meta envia (é gigante)
    print("Novo evento recebido:", body)

    # REGRA DE OURO DA META: DEVE retornar 200 OK imediatamente.
    # Se demorar pra responder, a Meta acha que meu servidor caiu e fica tentando reenviar a mensagem.
    return Response(status_code=status.HTTP_200_OK)