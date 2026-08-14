from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_viagem import RegistrarViagemUseCase


def test_registrar_viagem_sem_destino(db):

    # Carrega as var que serão usadas
    repository = RegistroRepository()
    use_case = RegistrarViagemUseCase(repository)

    # Simula uma mensagem da IA
    resposta = AIResponseDTO(
        intent="registrar_viagem",
        dados={
            "origem": "São Paulo"
        },
        resposta=""
    )

    # Executa o use_case, pega o seu resultado e aplica validações
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=1,
        db=db
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == (
        "Preciso saber a origem e o destino da viagem."
    )