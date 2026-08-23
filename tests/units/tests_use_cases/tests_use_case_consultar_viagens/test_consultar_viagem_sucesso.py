from datetime import datetime, timedelta

from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.consultar_viagens import ConsultarViagensUseCase


def test_consultar_viagens_com_sucesso(db):

    # Cria e salva um usuário no banco de testes
    usuario = Usuario(
        telefone="5511333333333"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Carrega as dependências e variáveis utilizadas no teste
    repository = RegistroRepository()
    use_case = ConsultarViagensUseCase(repository)

    agora = datetime.utcnow()
    inicio = agora - timedelta(days=1)
    fim = agora + timedelta(days=1)

    # Registra a primeira viagem
    repository.salvar(
        usuario_id=usuario.id,
        tipo="viagem",
        dados={
            "origem": "São Paulo",
            "destino": "Aracaju",
            "quilometros": 2100,
            "valor_frete": 8500
        },
        db=db
    )

    # Registra a segunda viagem
    repository.salvar(
        usuario_id=usuario.id,
        tipo="viagem",
        dados={
            "origem": "Aracaju",
            "destino": "Salvador",
            "quilometros": 600,
            "valor_frete": 3200
        },
        db=db
    )

    # Simula a resposta estruturada que viria da IA
    resposta = AIResponseDTO(
        intent="consultar_viagens",
        dados={
            "data_inicio": inicio,
            "data_fim": fim
        },
        resposta="Consulta de viagens realizada."
    )

    # Executa o caso de uso
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=usuario.id,
        db=db
    )

    # Valida o resultado da consulta
    assert resultado["sucesso"] is True
    assert len(resultado["viagens"]) == 2
    assert resultado["viagens"][0].tipo == "viagem"
    assert resultado["viagens"][1].tipo == "viagem"