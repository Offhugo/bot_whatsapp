from fastapi import FastAPI, Request, Response, status, Depends, Body
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import engine, get_db
from pydantic import BaseModel
import os
import models

class MetaDTO(BaseModel):
    object: str
    entry: list

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# ESSA É A LINHA MÁGICA:
# Ela olha para o models.py e cria as tabelas no banco se elas não existirem
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="WhatsApp Bot API")

# Este token será colocado lá no painel da Meta depois.
VERIFY_TOKEN = os.getenv("WHATSAPP_TOKEN")

# 1. ROTA GET: Verificação da Meta
@app.get("/")
def home():
    return {"status": "Bot rodando perfeitamente!"}

# Lembrar de colocar validações robustas
# 2. ROTA POST: Receber Mensagens
@app.post("/webhook")
async def receber_mensagem_meta(payload: MetaDTO, db: Session = Depends(get_db)):
    """
        Aqui é onde a mágica acontece. Processa o JSON da Meta e salva no PostgreSQL.
        """
    # Transforma o objeto de volta em dicionário para sua lógica continuar funcionando!
    body = payload.dict()

    print("Novo evento recebido:", body)

    try:
        # 2. Navegando pela estrutura do JSON do WhatsApp
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        # Verifica se o evento realmente contém uma mensagem de usuário
        if "messages" in value:
            mensagem_meta = value["messages"][0]
            contato_meta = value["contacts"][0]

            telefone_cliente = contato_meta["wa_id"]
            texto_mensagem = mensagem_meta["text"]["body"]

            # 3. Lógica de Banco: Busca o usuário ou cria um novo
            usuario = db.query(models.Usuario).filter(models.Usuario.telefone == telefone_cliente).first()

            if not usuario:
                usuario = models.Usuario(telefone=telefone_cliente)
                db.add(usuario)
                db.commit()
                db.refresh(usuario)  # Atualiza o objeto com o ID gerado pelo banco

            # 4. Salva a mensagem no histórico do banco
            nova_mensagem = models.Mensagem(
                texto=texto_mensagem,
                usuario_id=usuario.id
            )
            db.add(nova_mensagem)
            db.commit()

            print(f" Sucesso: Mensagem de {telefone_cliente} salva no banco!")

        # A Meta EXIGE um retorno 200 OK rápido, senão ela acha que deu erro e tenta reenviar.
        return {"status": "success"}

    except Exception as e:
        print(f" Erro ao processar o webhook: {e}")
        return {"status": "error"}

