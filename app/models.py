from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Rever essa estretura de colunas

# 1. Tabela de Usuários (Clientes)
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    telefone = Column(String, unique=True, index=True)  # O ID do WhatsApp (ex: 557999315620)
    nome = Column(String, nullable=True)

    # Campo flexível para guardar preferências do cliente
    perfil_dinamico = Column(JSONB, default={})
    criado_em = Column(DateTime, default=datetime.utcnow)

    mensagens = relationship("Mensagem", back_populates="usuario")
    viagens = relationship("Viagem", back_populates="usuario")


# 2. Tabela de Histórico de Conversa (A memória da IA)
class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    remetente = Column(String)  # Pode ser 'usuario' ou 'ia'
    texto = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="mensagens")


# 3. Tabela de Negócios (Viagens/Transporte)
class Viagem(Base):
    __tablename__ = "viagens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column(
        String,
        default="cotacao")  # cotacao, agendada, em_transito, concluida

    # AQUI ESTÁ A MÁGICA: A IA vai extrair dados do texto e jogar neste JSON.
    # Ex: {"origem": "São Paulo", "destino": "Sergipe", "carga": "Soja", "valor_combinado": 5000}
    detalhes = Column(
        JSONB,
        default={})

    criado_em = Column(
        DateTime,
        default=datetime.utcnow)

    usuario = relationship(
        "Usuario",
        back_populates="viagens")


class Registro(Base):

    __tablename__ = "registros"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    tipo = Column(
        String,
        nullable=False
    )

    dados = Column(
        JSONB,
        nullable=False
    )

    criado_em = Column(
        DateTime,
        nullable=False
    )