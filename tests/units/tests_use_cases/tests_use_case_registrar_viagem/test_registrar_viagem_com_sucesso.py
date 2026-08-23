from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_viagem import RegistrarViagemUseCase


def test_registrar_viagem_com_sucesso(db):

    # Cria e adiciona o user ao banco de testes
    usuario = Usuario(
        telefone="5511777777777"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # carrega var necessarias
    repository = RegistroRepository()
    use_case = RegistrarViagemUseCase(repository)

    # Cria e salva em uma var uma possivel resposta da IA
    resposta = AIResponseDTO(
        intent="registrar_viagem",
        dados={
            "origem": "São Paulo",
            "destino": "Aracaju",
            "quilometros": 2100,
            "valor_frete": 8500
        },
        resposta="Viagem registrada com sucesso."
    )

    # Aplica o use_case e caso sucesso, is true
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=usuario.id,
        db=db
    )

    assert resultado["sucesso"] is True