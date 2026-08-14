from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_abastecimento import RegistrarAbastecimentoUseCase


def test_registrar_abastecimento_com_sucesso(db):

    # Usuario ficticio criado e adicionado ao banco de testes
    usuario = Usuario(
        telefone="5511888888888"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Caregando var a ser usada nos testes
    repository = RegistroRepository()
    use_case = RegistrarAbastecimentoUseCase(repository)

    # extraindo resposta da IA
    resposta = AIResponseDTO(
        intent="registrar_abastecimento",
        dados={
            "valor": 350.50
        },
        resposta="Abastecimento registrado com sucesso."
    )

    # Executando a use case para preencher valor abastecido e testando a mesma
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=usuario.id,
        db=db
    )

    assert resultado["sucesso"] is True