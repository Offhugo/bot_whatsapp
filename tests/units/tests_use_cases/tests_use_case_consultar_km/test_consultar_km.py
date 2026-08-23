from datetime import datetime, timedelta

from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.consultar_km import ConsultarKMUseCase


def test_consultar_km_com_sucesso(db):

    # Cria e salva um usuário no banco de testes
    usuario = Usuario(
        telefone="5511555555555"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Carrega as dependências e variáveis utilizadas no teste
    repository = RegistroRepository()
    use_case = ConsultarKMUseCase(repository)

    agora = datetime.utcnow()
    inicio = agora - timedelta(days=1)
    fim = agora + timedelta(days=1)

    # Registra o primeiro deslocamento em quilômetros
    repository.salvar(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 430
        },
        db=db
    )

    # Registra o segundo deslocamento em quilômetros
    repository.salvar(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 820
        },
        db=db
    )

    # Registra um abastecimento para garantir que a consulta filtre pelo tipo correto
    repository.salvar(
        usuario_id=usuario.id,
        tipo="abastecimento",
        dados={
            "valor": 350
        },
        db=db
    )

    # Simula a resposta estruturada que viria da IA
    resposta = AIResponseDTO(
        intent="consultar_km",
        dados={
            "data_inicio": inicio,
            "data_fim": fim
        },
        resposta="Consulta de quilometragem realizada."
    )

    # Executa o caso de uso
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=usuario.id,
        db=db
    )

    # Valida o resultado da consulta
    assert resultado["sucesso"] is True
    assert resultado["total_km"] == 1250