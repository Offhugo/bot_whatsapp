from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from datetime import datetime

from app.models import Usuario, Empresa, Viagem, Registro

from app.models import (
    Empresa,
    Registro,
    Usuario,
    UsuarioEmpresa
)


def test_usuario_pode_ser_vinculado_a_duas_empresas(db):
    # Cria um usuário que pode trabalhar para diferentes empresas.
    usuario = Usuario(
        telefone="5511999990001",
        nome="João",
        perfil="motorista"
    )

    empresa_a = Empresa(
        nome="Transportadora A",
        cnpj="11111111000101"
    )

    empresa_b = Empresa(
        nome="Transportadora B",
        cnpj="22222222000102"
    )

    db.add_all([
        usuario,
        empresa_a,
        empresa_b
    ])

    db.commit()

    # Cria os dois vínculos do mesmo motorista.
    vinculo_a = UsuarioEmpresa(
        usuario_id=usuario.id,
        empresa_id=empresa_a.id
    )

    vinculo_b = UsuarioEmpresa(
        usuario_id=usuario.id,
        empresa_id=empresa_b.id
    )

    db.add_all([
        vinculo_a,
        vinculo_b
    ])

    db.commit()

    # O mesmo usuário pode estar associado
    # a mais de uma empresa.
    vinculos = (
        db.query(UsuarioEmpresa)
        .filter(
            UsuarioEmpresa.usuario_id == usuario.id
        )
        .all()
    )

    assert len(vinculos) == 2


def test_usuario_nao_pode_ter_vinculo_duplicado_com_a_mesma_empresa(db):
    # Cria o usuário e a empresa.
    usuario = Usuario(
        telefone="5511999990002",
        nome="Carlos",
        perfil="motorista"
    )

    empresa = Empresa(
        nome="Transportadora C",
        cnpj="33333333000103"
    )

    db.add_all([
        usuario,
        empresa
    ])

    db.commit()

    # Primeiro vínculo válido.
    primeiro_vinculo = UsuarioEmpresa(
        usuario_id=usuario.id,
        empresa_id=empresa.id
    )

    db.add(primeiro_vinculo)
    db.commit()

    # Tenta criar exatamente o mesmo vínculo novamente.
    segundo_vinculo = UsuarioEmpresa(
        usuario_id=usuario.id,
        empresa_id=empresa.id
    )

    db.add(segundo_vinculo)

    # O UniqueConstraint deve impedir a duplicação.
    with pytest.raises(IntegrityError):
        db.commit()

    # Recupera a sessão após a exceção.
    db.rollback()


def test_vinculo_pode_ser_desativado_sem_ser_excluido(db):
    usuario = Usuario(
        telefone="5511999990003",
        nome="Pedro",
        perfil="motorista"
    )

    empresa = Empresa(
        nome="Transportadora D",
        cnpj="44444444000104"
    )

    db.add_all([
        usuario,
        empresa
    ])

    db.commit()

    vinculo = UsuarioEmpresa(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        ativo=True
    )

    db.add(vinculo)
    db.commit()

    # O vínculo é encerrado sem apagar seu histórico.
    vinculo.ativo = False

    db.commit()

    vinculo_salvo = (
        db.query(UsuarioEmpresa)
        .filter(
            UsuarioEmpresa.id == vinculo.id
        )
        .first()
    )

    assert vinculo_salvo is not None
    assert vinculo_salvo.ativo is False


def test_registro_pode_ser_independente_da_empresa(db):
    # Motorista independente pode registrar uma operação
    # sem estar associada a uma empresa.
    usuario = Usuario(
        telefone="5511999990004",
        nome="Marcos",
        perfil="motorista"
    )

    db.add(usuario)
    db.commit()

    registro = Registro(
        usuario_id=usuario.id,
        empresa_id=None,
        tipo="km",
        dados={
            "quilometros": 430
        },
        criado_em=datetime.utcnow()
    )

    db.add(registro)
    db.commit()

    registro_salvo = (
        db.query(Registro)
        .filter(
            Registro.id == registro.id
        )
        .first()
    )

    assert registro_salvo is not None
    assert registro_salvo.empresa_id is None


def test_registro_pode_ser_associado_a_uma_empresa(db):
    usuario = Usuario(
        telefone="5511999990005",
        nome="Rafael",
        perfil="motorista"
    )

    empresa = Empresa(
        nome="Transportadora E",
        cnpj="55555555000105"
    )

    db.add_all([
        usuario,
        empresa
    ])

    db.commit()

    registro = Registro(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        tipo="viagem",
        dados={
            "origem": "Aracaju",
            "destino": "Salvador"
        },
        criado_em=datetime.utcnow()
    )

    db.add(registro)
    db.commit()

    registro_salvo = (
        db.query(Registro)
        .filter(
            Registro.id == registro.id
        )
        .first()
    )

    assert registro_salvo is not None
    assert registro_salvo.usuario_id == usuario.id
    assert registro_salvo.empresa_id == empresa.id

def test_viagem_pode_ser_associada_a_empresa(db):
    usuario = Usuario(
        telefone="5511999999999",
        nome="Motorista Teste"
    )

    empresa = Empresa(
        nome="Empresa A",
        cnpj="12345678000199"
    )

    db.add(usuario)
    db.add(empresa)
    db.commit()

    viagem = Viagem(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        status="em_andamento",
        detalhes={
            "origem": "Aracaju",
            "destino": "Salvador"
        },
        criado_em=datetime.utcnow()
    )

    db.add(viagem)
    db.commit()
    db.refresh(viagem)

    assert viagem.usuario_id == usuario.id
    assert viagem.empresa_id == empresa.id
    assert viagem.empresa == empresa


def test_viagem_pode_existir_sem_empresa(db):
    usuario = Usuario(
        telefone="5511888888888",
        nome="Motorista Independente"
    )

    db.add(usuario)
    db.commit()

    viagem = Viagem(
        usuario_id=usuario.id,
        empresa_id=None,
        status="em_andamento",
        detalhes={
            "origem": "Aracaju",
            "destino": "Maceió"
        },
        criado_em=datetime.utcnow()
    )

    db.add(viagem)
    db.commit()
    db.refresh(viagem)

    assert viagem.usuario_id == usuario.id
    assert viagem.empresa_id is None
    assert viagem.empresa is None


def test_registro_pode_ser_associado_a_viagem(db):
    usuario = Usuario(
        telefone="5511777777777",
        nome="Motorista"
    )

    empresa = Empresa(
        nome="Empresa B",
        cnpj="98765432000188"
    )

    db.add(usuario)
    db.add(empresa)
    db.commit()

    viagem = Viagem(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        status="em_andamento",
        detalhes={
            "origem": "Aracaju",
            "destino": "Recife"
        },
        criado_em=datetime.utcnow()
    )

    db.add(viagem)
    db.commit()
    db.refresh(viagem)

    registro = Registro(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        viagem_id=viagem.id,
        tipo="km",
        dados={
            "quilometros": 500
        },
        criado_em=datetime.utcnow()
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    assert registro.usuario_id == usuario.id
    assert registro.empresa_id == empresa.id
    assert registro.viagem_id == viagem.id
    assert registro.viagem == viagem


def test_registro_pode_existir_sem_viagem(db):
    usuario = Usuario(
        telefone="5511666666666",
        nome="Motorista"
    )

    empresa = Empresa(
        nome="Empresa C",
        cnpj="11222333000144"
    )

    db.add(usuario)
    db.add(empresa)
    db.commit()

    registro = Registro(
        usuario_id=usuario.id,
        empresa_id=empresa.id,
        viagem_id=None,
        tipo="km",
        dados={
            "quilometros": 200
        },
        criado_em=datetime.utcnow()
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    assert registro.usuario_id == usuario.id
    assert registro.empresa_id == empresa.id
    assert registro.viagem_id is None
    assert registro.viagem is None