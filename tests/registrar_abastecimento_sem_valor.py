from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_abastecimento import RegistrarAbastecimentoUseCase


def test_registrar_abastecimento_sem_valor(db):

    repository = RegistroRepository()
    use_case = RegistrarAbastecimentoUseCase(repository)

    resposta = AIResponseDTO(
        intent="registrar_abastecimento",
        dados={},
        resposta=""
    )

    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=1,
        db=db
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Qual foi o valor do abastecimento?"