from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_km import RegistrarKMUseCase


def test_registrar_km_sem_quilometragem(db):

    # Var para o código funcionar(aplicando a injeção de dependencias de maneira correta)
    repository = RegistroRepository()
    use_case = RegistrarKMUseCase(repository)

    # Criando uma resposta completa da IA
    resposta = AIResponseDTO(
        intent="registrar_km",
        dados={},  # A IA não conseguiu extrair os quilômetros.
        resposta=""
    )

    # Aplicando o use_case na resposta
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=1,
        db=db
    )

    # Aplicando validações
    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Quantos quilômetros foram percorridos?"