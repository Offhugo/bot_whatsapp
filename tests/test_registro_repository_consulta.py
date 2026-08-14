from datetime import datetime, timedelta

from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository


def test_buscar_registros_por_tipo_e_periodo(db):

    # Cria e salva um user no banco de testes
    usuario = Usuario(
        telefone="5511666666666"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Carrega as var que usamos no teste
    repository = RegistroRepository()

    agora = datetime.utcnow()
    inicio = agora - timedelta(days=1)
    fim = agora + timedelta(days=1)

    # Registra os kms
    repository.salvar(
        usuario_id=usuario.id,
        tipo="km",
        dados={
            "quilometros": 430
        },
        db=db
    )

    # Resgistra o valor abastecido
    repository.salvar(
        usuario_id=usuario.id,
        tipo="abastecimento",
        dados={
            "valor": 350
        },
        db=db
    )

    # Carrega o resultado do metodo de busca para uma var testavel
    registros = repository.buscar_por_tipo_e_periodo(
        usuario_id=usuario.id,
        tipo="km",
        data_inicio=inicio,
        data_fim=fim,
        db=db
    )

    # Validações corretas
    assert len(registros) == 1
    assert registros[0].tipo == "km"
    assert registros[0].dados["quilometros"] == 430