from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository
from app.use_cases.registrar_km import RegistrarKMUseCase
from app.schemas.ai_response import AIResponseDTO


def test_registrar_km_com_sucesso(db):

    # Criação do user para testes
    usuario = Usuario(
        telefone="5511999999999"
    )

    # adicionando o user ao banco
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Carrega as var que vão ser passadas para o código ser testado
    repository = RegistroRepository()
    use_case = RegistrarKMUseCase(repository)

    # Extrai a informação que queremos, no caso os Kms
    resposta = AIResponseDTO(
        intent="registrar_km",
        dados={
            "quilometros": 430
        },
        resposta="Registro de quilometragem realizado com sucesso."
    )

    # Resultado das operações
    resultado = use_case.executar(
        resposta=resposta,
        usuario_id=usuario.id,
        db=db
    )

    # Validação final
    assert resultado["sucesso"] is True