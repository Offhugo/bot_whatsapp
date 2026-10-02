from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


# ============================================================
# 1. Usuário
# ============================================================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    telefone = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    nome = Column(
        String,
        nullable=True
    )

    # Perfil do usuário.
    # No MVP:
    # - motorista
    # - gerente
    perfil = Column(
        String,
        nullable=False,
        default="motorista"
    )

    # Campo flexível para preferências
    # e informações complementares do usuário.
    perfil_dinamico = Column(
        JSONB,
        default={}
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    mensagens = relationship(
        "Mensagem",
        back_populates="usuario"
    )

    viagens = relationship(
        "Viagem",
        back_populates="usuario"
    )

    registros = relationship(
        "Registro",
        back_populates="usuario"
    )

    empresas_vinculos = relationship(
        "UsuarioEmpresa",
        back_populates="usuario"
    )


# ============================================================
# 2. Empresa
# ============================================================

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String,
        nullable=False
    )

    cnpj = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    usuarios_vinculos = relationship(
        "UsuarioEmpresa",
        back_populates="empresa"
    )

    registros = relationship(
        "Registro",
        back_populates="empresa"
    )

    viagens = relationship(
        "Viagem",
        back_populates="empresa"
    )


# ============================================================
# 3. Vínculo entre usuário e empresa
# ============================================================

class UsuarioEmpresa(Base):
    __tablename__ = "usuarios_empresas"

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

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=False
    )

    # Permite encerrar o vínculo sem apagar
    # o histórico da associação.
    ativo = Column(
        Boolean,
        nullable=False,
        default=True
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    usuario = relationship(
        "Usuario",
        back_populates="empresas_vinculos"
    )

    empresa = relationship(
        "Empresa",
        back_populates="usuarios_vinculos"
    )

    # Impede o mesmo usuário de possuir
    # duas associações iguais com a mesma empresa.
    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "empresa_id",
            name="uq_usuario_empresa"
        ),
    )


# ============================================================
# 4. Histórico de conversa
# ============================================================

class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id")
    )

    remetente = Column(
        String
    )

    texto = Column(
        Text
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    usuario = relationship(
        "Usuario",
        back_populates="mensagens"
    )


# ============================================================
# 5. Viagem
# ============================================================

class Viagem(Base):
    __tablename__ = "viagens"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id")
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=True
    )

    status = Column(
        String,
        default="cotacao"
    )

    detalhes = Column(
        JSONB,
        default={}
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    usuario = relationship(
        "Usuario",
        back_populates="viagens"
    )

    empresa = relationship(
        "Empresa",
        back_populates="viagens"
    )

    registros = relationship(
        "Registro",
        back_populates="viagem"
    )


# ============================================================
# 6. Registro operacional
# ============================================================

class Registro(Base):
    __tablename__ = "registros"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    viagem_id = Column(
        Integer,
        ForeignKey("viagens.id"),
        nullable=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    # Opcional porque o motorista pode
    # registrar uma operação independente.
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=True
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

    usuario = relationship(
        "Usuario",
        back_populates="registros"
    )

    empresa = relationship(
        "Empresa",
        back_populates="registros"
    )

    viagem = relationship(
        "Viagem",
        back_populates="registros"
    )