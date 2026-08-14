from datetime import datetime, timedelta

from app.models import Usuario, Registro
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.consultar_km import ConsultarKMUseCase


def test_consultar_km_ignora_registro_fora_do_periodo(db):

    # Cria e salva um usuário no banco de testes
    usuario = Usuario(
        telefone="5511444444444"
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

    # Registro que está dentro da janela de consulta
    registro_dentro = Registro(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 430
        },
        criado_em=agora
    )

    # Registro que está fora da janela de consulta
    registro_fora = Registro(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 1000
        },
        criado_em=agora - timedelta(days=10)
    )

    db.add_all([
        registro_dentro,
        registro_fora
    ])

    db.commit()

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

    # Apenas o registro dentro da janela deve ser considerado
    assert resultado["sucesso"] is True
    assert resultado["total_km"] == 430