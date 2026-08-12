from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository


def test_salvar_registro(db):

    # Criando um usuario para os testes
    usuario = Usuario(
        telefone="5511999999999"
    )

    # Adicionando esse user no banco
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    repository = RegistroRepository()

    # Testando de fato o repository para salvar
    registro = repository.salvar(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 430
        },
        db=db
    )

    # Validações em cima dos dados salvos
    assert registro is not None
    assert registro.tipo == "km"
    assert registro.dados["quilometros"] == 430