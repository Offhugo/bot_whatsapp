from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.consultar_viagens import ConsultarViagensUseCase


def test_consultar_viagens_sem_periodo(db):

    # Carrega as dependências utilizadas no teste
    repository = RegistroRepository()
    use_case = ConsultarViagensUseCase(repository)

    # Simula uma resposta da IA sem informar o período
    resposta = AIResponseDTO(
        intent="consultar_viagens",
        dados={},
        resposta=""
    )

    # Executa o caso de uso
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=1,
        db=db
    )

    # Valida que a consulta não foi executada
    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == (
        "Preciso saber qual período você deseja consultar."
    )