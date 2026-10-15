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

    # ⚡ NOVO: Timezone preferido do usuário (Item 10)
    timezone = Column(
        String,
        nullable=False,
        default="America/Fortaleza"
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

    # ⚡ NOVO: Histórico de conversas (Item 3)
    conversas = relationship(
        "Conversa",
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

    # ⚡ NOVO: Relacionamento com conversas (Item 9)
    conversas = relationship(
        "Conversa",
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

    # ⚡ NOVO: Relacionamento com conversas (Item 9)
    conversas = relationship(
        "Conversa",
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


# ============================================================
# 7. Conversa (Item 3 - Histórico)
# ============================================================

class Conversa(Base):
    """
    Armazena histórico de conversas com usuários.

    Permite manter contexto entre mensagens para tornar
    as conversas mais naturais e contextualizadas.

    O JSONB contexto armazena dados heterogêneos e variáveis
    (ex: km, distância, ajudantes, etc) que mudam conforme
    a natureza de cada conversa.
    """
    __tablename__ = "conversas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )

    # ⚡ NOVO: Referências diretas a viagem e empresa (Item 9)
    # Permite queries rápidas e integridade referencial
    viagem_id = Column(
        Integer,
        ForeignKey("viagens.id"),
        nullable=True,
        index=True
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=True,
        index=True
    )

    # Histórico de mensagens (array de {role, content, timestamp})
    mensagens = Column(
        JSONB,
        nullable=False,
        default=[]
    )

    # Contexto flexível (dados heterogêneos e variáveis)
    # Exemplos: {km: 150, distancia: 200, ajudantes: 2, etc}
    contexto = Column(
        JSONB,
        nullable=True
    )

    # Timestamps
    criado_em = Column(
        DateTime,
        nullable=False
    )

    atualizado_em = Column(
        DateTime,
        nullable=False
    )

    # Relationships
    usuario = relationship(
        "Usuario",
        back_populates="conversas"
    )

    # ⚡ NOVO: Relationships para viagem e empresa (Item 9)
    viagem = relationship(
        "Viagem",
        back_populates="conversas"
    )

    empresa = relationship(
        "Empresa",
        back_populates="conversas"
    )