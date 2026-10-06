from unittest.mock import MagicMock

from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_km import RegistrarKMUseCase
from app.utils.validation_limits import MAX_QUILOMETROS_POR_REGISTRO


def criar_resposta(quilometros):
    return AIResponseDTO(
        intent="registrar_km",
        dados={
            "quilometros": quilometros
        },
        resposta="Quilometragem registrada."
    )


def criar_use_case():
    repository = MagicMock()
    use_case = RegistrarKMUseCase(repository)

    return use_case, repository


def test_registrar_km_com_valor_inteiro_valido():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(430)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is True
    repository.salvar.assert_called_once()


def test_registrar_km_com_valor_decimal_valido():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(430.5)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is True
    repository.salvar.assert_called_once()


def test_registrar_km_rejeita_string_numerica():
    use_case, repository = criar_use_case()

    resposta = criar_resposta("430")

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_zero():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(0)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_valor_negativo():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(-50)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_booleano():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(True)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_nan():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(float("nan"))

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_infinito():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(float("inf"))

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_valor_acima_do_limite():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        MAX_QUILOMETROS_POR_REGISTRO + 1
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_km_rejeita_campo_ausente():
    use_case, repository = criar_use_case()

    resposta = AIResponseDTO(
        intent="registrar_km",
        dados={},
        resposta="Preciso da quilometragem."
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == (
        "Quantos quilômetros foram percorridos?"
    )
    repository.salvar.assert_not_called()