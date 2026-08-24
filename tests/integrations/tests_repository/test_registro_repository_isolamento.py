from datetime import datetime, timedelta

from app.models import Usuario
from app.repositories.registro_repository import RegistroRepository


def test_registro_repository_isola_dados_entre_usuarios(db):

    # Cria e salva o primeiro usuário
    usuario_a = Usuario(
        telefone="5511111111111"
    )

    # Cria e salva o segundo usuário
    usuario_b = Usuario(
        telefone="5522222222222"
    )

    # Adiciona e atualiza no banco os users de teste
    db.add_all([
        usuario_a,
        usuario_b
    ])

    db.commit()

    db.refresh(usuario_a)
    db.refresh(usuario_b)

    # Carrega o repository utilizado no teste
    repository = RegistroRepository()

    agora = datetime.utcnow()
    inicio = agora - timedelta(days=1)
    fim = agora + timedelta(days=1)

    # Registra um KM para o usuário A
    repository.salvar(
        usuario_id=usuario_a.id,
        tipo="km",
        dados={
            "quilometros": 430
        },
        db=db
    )

    # Registra outro KM para o usuário B
    repository.salvar(
        usuario_id=usuario_b.id,
        tipo="km",
        dados={
            "quilometros": 900
        },
        db=db
    )

    # Consulta os registros do usuário A
    registros_usuario_a = (
        repository.buscar_por_tipo_e_periodo(
            usuario_id=usuario_a.id,
            tipo="km",
            data_inicio=inicio,
            data_fim=fim,
            db=db
        )
    )

    # Valida que somente os dados do usuário A foram retornados
    assert len(registros_usuario_a) == 1
    assert registros_usuario_a[0].usuario_id == usuario_a.id
    assert registros_usuario_a[0].dados["quilometros"] == 430

    # Garante que o registro do usuário B não apareceu
    assert registros_usuario_a[0].dados["quilometros"] != 900