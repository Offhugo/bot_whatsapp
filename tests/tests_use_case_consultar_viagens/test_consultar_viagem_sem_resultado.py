from datetime import datetime, timedelta

from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.consultar_viagens import ConsultarViagensUseCase


def test_consultar_viagens_sem_resultado(db):

    # Cria e salva um usuário no banco de testes
    usuario = Usuario(
        telefone="5511222222222"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Carrega as dependências utilizadas no teste
    repository = RegistroRepository()
    use_case = ConsultarViagensUseCase(repository)

    agora = datetime.utcnow()
    inicio = agora - timedelta(days=1)
    fim = agora + timedelta(days=1)

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

    # Valida que a consulta foi válida, mas não encontrou registros
    assert resultado["sucesso"] is True
    assert resultado["viagens"] == []